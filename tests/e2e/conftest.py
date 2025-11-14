"""
E2E test configuration and fixtures for LunarCrush Lambda function testing.

This module provides fixtures and configuration specifically for end-to-end tests
that require real Docker environments, LocalStack integration, and complete workflow validation.
"""

import os
import json
import time
import pytest
import subprocess
import threading
import requests
from typing import Dict, Any, List, Optional, Generator
from unittest.mock import Mock, patch

# Load environment variables from test configuration file
try:
    from dotenv import load_dotenv
    # Try to load from test environment file first
    test_env_file = os.path.join(os.path.dirname(__file__), '..', '.env.test')
    if os.path.exists(test_env_file):
        load_dotenv(test_env_file)
        print(f"✅ Loaded test environment from {test_env_file}")
    else:
        # Fallback to local environment file
        load_dotenv('.env.local')
        print("⚠️  Using local environment file (.env.local) - consider using .env.test for e2e tests")
except ImportError:
    # Fallback if dotenv is not available
    print("⚠️  dotenv not available - environment variables must be set manually")

import docker
from docker.client import DockerClient
from docker.errors import DockerException, APIError

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.lunarcrush_client import LunarCrushClient
from src.adapters.s3_storage import S3Storage


# E2E test configuration
E2E_TEST_CONFIG = {
    "docker_compose_file": "docker-compose.yml",
    "lambda_endpoint": "http://localhost:9000",
    "localstack_endpoint": "http://localhost:4566",
    "test_bucket_name": "local-test-bucket",
    "aws_region": "us-east-1",
    "test_symbols": ["BTC", "ETH", "ADA", "DOT", "LINK"],
    "large_symbol_set": [f"BTC{i:02d}" for i in range(1, 51)],  # 50 symbols for performance testing
    "startup_timeout": 120,  # seconds
    "request_timeout": 30,   # seconds
    "performance_threshold": 30,  # seconds for 50 symbols
    "health_check_interval": 5,  # seconds
    "max_retries": 3,
    "retry_delay": 2,  # seconds
}


def is_e2e_test_enabled() -> bool:
    """Check if E2E tests are enabled via environment variable."""
    return os.getenv("ENABLE_E2E_TESTS", "false").lower() == "true"


def has_docker() -> bool:
    """Check if Docker is available and running."""
    try:
        client = docker.from_env()
        client.ping()
        return True
    except (DockerException, Exception):
        return False


def has_docker_compose() -> bool:
    """Check if docker-compose is available."""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_port_available(port: int, host: str = "localhost") -> bool:
    """Check if a port is available on the host."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


@pytest.fixture(scope="session")
def e2e_config():
    """Fixture providing E2E test configuration."""
    # Validate E2E test requirements - fail if conditions are not met
    if not is_e2e_test_enabled():
        raise Exception("E2E tests are disabled. Set ENABLE_E2E_TESTS=true to enable.")
    
    if not has_docker():
        raise Exception("Docker is not available or not running.")
    
    if not has_docker_compose():
        raise Exception("docker-compose is not available.")
    
    # Check if required ports are available
    if not is_port_available(9000):
        raise Exception("Port 9000 is already in use. Required for Lambda endpoint.")
    
    if not is_port_available(4566):
        raise Exception("Port 4566 is already in use. Required for LocalStack endpoint.")
    
    return E2E_TEST_CONFIG


@pytest.fixture(scope="session")
def docker_environment(e2e_config):
    """Fixture to manage Docker environment for E2E tests."""
    compose_file = e2e_config["docker_compose_file"]
    
    # Start Docker environment
    print(f"Starting Docker environment with {compose_file}...")
    try:
        # Start services
        subprocess.run(
            ["docker-compose", "-f", compose_file, "up", "-d"],
            check=True,
            timeout=e2e_config["startup_timeout"]
        )
        
        # Wait for services to be ready
        print("Waiting for services to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < e2e_config["startup_timeout"]:
            try:
                # Check Lambda endpoint
                lambda_response = requests.get(
                    f"{e2e_config['lambda_endpoint']}/2015-03-31/functions/function/invocations",
                    timeout=5
                )
                
                # Check LocalStack endpoint
                localstack_response = requests.get(
                    f"{e2e_config['localstack_endpoint']}/health",
                    timeout=5
                )
                
                if lambda_response.status_code in [200, 404] and localstack_response.status_code == 200:
                    print("Services are ready!")
                    break
                    
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(e2e_config["health_check_interval"])
        else:
            pytest.fail("Services did not become ready within timeout period.")
        
        yield e2e_config
        
    finally:
        # Clean up Docker environment
        print("Cleaning up Docker environment...")
        try:
            subprocess.run(
                ["docker-compose", "-f", compose_file, "down", "-v"],
                check=True,
                timeout=60
            )
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to clean up Docker environment: {e}")


@pytest.fixture
def lambda_client(docker_environment):
    """Fixture providing a client for Lambda function invocation."""
    endpoint = docker_environment["lambda_endpoint"]
    
    class LambdaClient:
        def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
            """Invoke the Lambda function with the given payload."""
            url = f"{endpoint}/2015-03-31/functions/function/invocations"
            
            response = requests.post(
                url,
                json=payload,
                timeout=docker_environment["request_timeout"]
            )
            
            if response.status_code != 200:
                raise Exception(f"Lambda invocation failed: {response.status_code} - {response.text}")
            
            return response.json()
    
    return LambdaClient()


@pytest.fixture
def localstack_s3_client(docker_environment):
    """Fixture providing an S3 client connected to LocalStack."""
    import boto3
    
    return S3Storage(
        bucket_name=docker_environment["test_bucket_name"],
        endpoint_url=docker_environment["localstack_endpoint"],
        aws_region=docker_environment["aws_region"]
    )


@pytest.fixture
def performance_monitor():
    """Fixture to monitor performance during E2E tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.measurements = []
            self.start_time = None
        
        def start_measurement(self, operation: str):
            """Start measuring an operation."""
            self.start_time = time.time()
            return {"operation": operation, "start_time": self.start_time}
        
        def end_measurement(self, measurement: Dict, success: bool = True, error: str = None):
            """End measuring an operation."""
            end_time = time.time()
            duration = end_time - measurement["start_time"]
            
            result = {
                "operation": measurement["operation"],
                "duration": duration,
                "success": success,
                "timestamp": end_time
            }
            
            if error:
                result["error"] = error
            
            self.measurements.append(result)
            return result
        
        def get_stats(self) -> Dict[str, Any]:
            """Get performance statistics."""
            if not self.measurements:
                return {}
            
            durations = [m["duration"] for m in self.measurements]
            successful_ops = [m for m in self.measurements if m["success"]]
            
            return {
                "total_operations": len(self.measurements),
                "successful_operations": len(successful_ops),
                "failed_operations": len(self.measurements) - len(successful_ops),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "total_duration": sum(durations),
                "success_rate": len(successful_ops) / len(self.measurements)
            }
    
    return PerformanceMonitor()


@pytest.fixture
def data_validator():
    """Fixture to validate data structures and content."""
    class DataValidator:
        def validate_lambda_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
            """Validate Lambda response structure."""
            errors = []
            
            # Check basic structure
            if not isinstance(response, dict):
                errors.append("Response must be a dictionary")
                return {"valid": False, "errors": errors}
            
            # Check for required fields
            required_fields = ["statusCode", "headers", "body"]
            for field in required_fields:
                if field not in response:
                    errors.append(f"Missing required field: {field}")
            
            # Check status code
            if response.get("statusCode") != 200:
                errors.append(f"Expected status code 200, got {response.get('statusCode')}")
            
            # Parse and validate body
            try:
                body = json.loads(response.get("body", "{}"))
                
                if not isinstance(body, dict):
                    errors.append("Body must be a JSON object")
                else:
                    # Check for success flag
                    if not body.get("success"):
                        errors.append("Response indicates failure")
                    
                    # Check for data field
                    if "data" not in body:
                        errors.append("Missing 'data' field in response body")
                    else:
                        data = body["data"]
                        
                        # Validate metrics structure
                        if "metrics" not in data:
                            errors.append("Missing 'metrics' field in response data")
                        elif not isinstance(data["metrics"], list):
                            errors.append("'metrics' must be a list")
                        
                        # Validate metadata structure
                        if "metadata" not in data:
                            errors.append("Missing 'metadata' field in response data")
                        elif not isinstance(data["metadata"], dict):
                            errors.append("'metadata' must be a dictionary")
                        
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in response body: {e}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
        
        def validate_metrics_structure(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Validate individual metrics structure."""
            errors = []
            
            if not isinstance(metrics, list):
                errors.append("Metrics must be a list")
                return {"valid": False, "errors": errors}
            
            for i, metric in enumerate(metrics):
                if not isinstance(metric, dict):
                    errors.append(f"Metric {i} must be a dictionary")
                    continue
                
                # Check for required fields in each metric
                required_fields = ["symbol", "current_metrics", "momentum_metrics", "timestamp"]
                for field in required_fields:
                    if field not in metric:
                        errors.append(f"Metric {i} missing required field: {field}")
                
                # Validate current_metrics
                if "current_metrics" in metric:
                    current = metric["current_metrics"]
                    current_fields = [
                        "interactions_24h", "social_volume_24h", "social_dominance",
                        "galaxy_score", "sentiment", "alt_rank"
                    ]
                    for field in current_fields:
                        if field not in current:
                            errors.append(f"Metric {i} missing current_metrics field: {field}")
                
                # Validate momentum_metrics
                if "momentum_metrics" in metric:
                    momentum = metric["momentum_metrics"]
                    momentum_fields = [
                        "galaxy_score_trend", "alt_rank_trend", "sentiment_trend",
                        "interactions_trend", "social_dominance_trend", "volume_trend"
                    ]
                    for field in momentum_fields:
                        if field not in momentum:
                            errors.append(f"Metric {i} missing momentum_metrics field: {field}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
    
    return DataValidator()


@pytest.fixture
def test_symbols(e2e_config):
    """Fixture providing test symbols for E2E testing."""
    return e2e_config["test_symbols"]


@pytest.fixture
def large_symbol_set(e2e_config):
    """Fixture providing a large set of symbols for performance testing."""
    return e2e_config["large_symbol_set"]


# E2E test markers
def pytest_configure(config):
    """Configure pytest with E2E test markers."""
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests requiring Docker environment"
    )
    config.addinivalue_line(
        "markers", "docker: marks tests that require Docker containers"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests that measure performance"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running E2E tests"
    )


# Note: E2E tests will fail if requirements are not met, following test rules that tests should either pass or fail, never skip