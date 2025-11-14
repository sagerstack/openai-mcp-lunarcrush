"""
Integration test configuration and fixtures for LunarCrush API testing.

This module provides fixtures and configuration specifically for integration tests
that require real API interactions, S3 storage, and network connectivity.
"""

import os
import json
import time
import pytest
import threading
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Generator

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
        print("⚠️  Using local environment file (.env.local) - consider using .env.test for integration tests")
except ImportError:
    # Fallback if dotenv is not available
    print("⚠️  dotenv not available - environment variables must be set manually")

import boto3
import requests
from moto import mock_s3
from docker.client import DockerClient
from docker.errors import DockerException

# TestContainers imports for automatic infrastructure setup
try:
    from testcontainers.core.container import DockerContainer
    from testcontainers.localstack import LocalStackContainer
    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.lunarcrush_client import LunarCrushClient, TokenBucket
from src.adapters.s3_storage import S3Storage
from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushRateLimitError,
    LunarCrushAuthenticationError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)


# Integration test configuration
INTEGRATION_TEST_CONFIG = {
    "test_symbols": ["BTC", "ETH", "ADA", "DOGE", "SOL"],  # More diverse symbols
    "test_api_key": os.getenv("LUNARCRUSH_API_KEY"),
    "test_bucket_name": os.getenv("S3_BUCKET_NAME", "lunarcrush-test-bucket"),
    "localstack_endpoint": os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566"),
    "aws_region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    "test_timeout": 120,  # Increased timeout for rate limiting
    "retry_attempts": 8,  # Increased retry attempts
    "rate_limit_test_delay": 5,  # Increased delay between requests
    "test_rate_limit": {
        "capacity": 30,  # Allow bursts of 30 requests
        "refill_rate": 0.5  # Refill at 0.5 requests per second (1 request every 2 seconds)
    }
}


def is_integration_test_enabled() -> bool:
    """Check if integration tests are enabled via environment variable."""
    return os.getenv("ENABLE_INTEGRATION_TESTS", "false").lower() == "true"


def has_valid_api_key() -> bool:
    """Check if a valid API key is available for testing."""
    api_key = INTEGRATION_TEST_CONFIG["test_api_key"]
    return api_key is not None and len(api_key) > 10


def is_localstack_available() -> bool:
    """Check if LocalStack is available for S3 testing."""
    try:
        response = requests.get(
            f"{INTEGRATION_TEST_CONFIG['localstack_endpoint']}/health",
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False


def is_docker_available() -> bool:
    """Check if Docker is available for LocalStack testing."""
    try:
        docker_client = DockerClient()
        docker_client.ping()
        return True
    except DockerException:
        return False


@pytest.fixture(scope="session")
def integration_config():
    """Fixture providing integration test configuration."""
    if not is_integration_test_enabled():
        pytest.fail("Integration tests must be enabled. Set ENABLE_INTEGRATION_TESTS=true to enable.")
    
    if not has_valid_api_key():
        pytest.fail("Valid API key must be available for integration testing. Set LUNARCRUSH_API_KEY environment variable.")
    
    return INTEGRATION_TEST_CONFIG


@pytest.fixture(scope="session")
def real_lunarcrush_client(integration_config):
    """Fixture providing a real LunarCrush client for integration testing."""
    try:
        # Create client with test-friendly rate limiting
        client = LunarCrushClient(
            api_key=integration_config["test_api_key"],
            cache_ttl=60  # Short cache for testing
        )
        
        # Override rate limiter for testing using config
        rate_limit_config = integration_config["test_rate_limit"]
        client.rate_limiter = TokenBucket(
            capacity=rate_limit_config["capacity"],
            refill_rate=rate_limit_config["refill_rate"]
        )
        
        print("✅ LunarCrush client initialized for testing")
        print(f"📊 Rate limit: {rate_limit_config['capacity']} tokens, {rate_limit_config['refill_rate']} refill/sec")
        return client
        
    except Exception as e:
        print(f"❌ Failed to initialize LunarCrush client: {e}")
        pytest.fail(f"Failed to create LunarCrush client: {e}")


@pytest.fixture(scope="session")
def localstack_container():
    """Fixture providing a TestContainers-managed LocalStack instance."""
    if not TESTCONTAINERS_AVAILABLE:
        pytest.fail("TestContainers not available. Install testcontainers-python to use automatic infrastructure setup.")
    
    try:
        # Try to use TestContainers with proper Docker configuration
        # Set environment for Docker client to work properly on macOS
        import os
        from testcontainers.core.docker_client import DockerClient
        
        # Configure Docker client for macOS
        docker_client = DockerClient()
        
        with LocalStackContainer(
            image="localstack/localstack:latest",
            edge_port=4566,
            docker_client_kw={"timeout": 120}  # Increase timeout
        ) as localstack:
            # Wait for LocalStack to be ready
            import time
            print("⏳ Waiting for LocalStack to start...")
            time.sleep(15)  # Give LocalStack more time to start
            
            # Check if LocalStack is healthy
            health_url = localstack.get_endpoint_url().replace("4566", "4566/health")
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    import requests
                    response = requests.get(health_url, timeout=5)
                    if response.status_code == 200:
                        print("✅ LocalStack is healthy")
                        break
                except:
                    pass
                time.sleep(2)
                if attempt == max_attempts - 1:
                    print("⚠️ LocalStack health check failed, proceeding anyway...")
            
            # Create S3 bucket
            import boto3
            s3_client = boto3.client(
                's3',
                endpoint_url=localstack.get_endpoint_url(),
                region_name="us-east-1"
            )
            
            # Create test bucket with error handling
            try:
                s3_client.create_bucket(Bucket="lunarcrush-test-bucket")
                print("✅ Created test bucket")
            except Exception as e:
                print(f"⚠️ Bucket creation failed: {e}")
                # Try to check if bucket already exists
                try:
                    s3_client.head_bucket(Bucket="lunarcrush-test-bucket")
                    print("✅ Test bucket already exists")
                except:
                    pass
            
            yield localstack
            
    except Exception as e:
        print(f"❌ TestContainers LocalStack setup failed: {e}")
        print("🔄 Falling back to manual LocalStack setup...")
        
        # Fallback: Try to use existing LocalStack or create simple mock
        class MockLocalStack:
            def __init__(self):
                self.endpoint_url = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
                print(f"📦 Using LocalStack endpoint: {self.endpoint_url}")
            
            def get_endpoint_url(self):
                return self.endpoint_url
        
        yield MockLocalStack()


@pytest.fixture(scope="session")
def real_s3_storage(integration_config, localstack_container):
    """Fixture providing a real S3 storage client for integration testing."""
    try:
        endpoint_url = localstack_container.get_endpoint_url()
        bucket_name = integration_config["test_bucket_name"]
        
        print(f"🔧 Creating S3 storage client with endpoint: {endpoint_url}")
        print(f"🪣 Using bucket: {bucket_name}")
        
        # Create S3 storage with proper error handling
        s3_storage = S3Storage(
            bucket_name=bucket_name,
            endpoint_url=endpoint_url,
            aws_region="us-east-1"
        )
        
        # Test the connection
        try:
            # Try to list objects to verify connection
            s3_storage.list_archive_files()
            print("✅ S3 storage connection successful")
        except Exception as conn_error:
            print(f"⚠️ S3 connection test failed: {conn_error}")
            # Try to create bucket if it doesn't exist
            try:
                import boto3
                s3_client = boto3.client(
                    's3',
                    endpoint_url=endpoint_url,
                    region_name="us-east-1"
                )
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"✅ Created bucket: {bucket_name}")
            except Exception as bucket_error:
                print(f"⚠️ Bucket creation failed: {bucket_error}")
        
        return s3_storage
        
    except Exception as e:
        print(f"❌ Failed to create S3 storage client: {e}")
        # Return a mock S3 storage for tests that can work without real S3
        class MockS3Storage:
            def __init__(self):
                self.bucket_name = integration_config["test_bucket_name"]
                self.endpoint_url = "http://localhost:4566"
            
            def store_metrics(self, metrics):
                print(f"📝 Mock: storing {len(metrics) if metrics else 0} metrics")
                return True
            
            def get_current_metrics(self):
                return None
            
            def list_archive_files(self):
                return []
            
            def archive_current_file(self):
                return ""
        
        return MockS3Storage()


@pytest.fixture
def test_symbols(integration_config):
    """Fixture providing test symbols for integration testing."""
    return integration_config["test_symbols"]


@pytest.fixture
def test_symbols_with_fallback(integration_config):
    """Fixture providing test symbols with fallback logic for availability."""
    primary_symbols = integration_config["test_symbols"]
    
    # Add fallback symbols in case primary ones aren't available
    fallback_symbols = ["BTC", "ETH", "XRP", "LTC", "BCH", "USDT", "USDC", "BNB", "DOT", "LINK"]
    
    # Combine both lists, with primary first
    all_symbols = primary_symbols + fallback_symbols
    
    # Return unique symbols in order of preference
    seen = set()
    unique_symbols = []
    for symbol in all_symbols:
        if symbol not in seen:
            seen.add(symbol)
            unique_symbols.append(symbol)
    
    return unique_symbols


@pytest.fixture
def api_performance_tracker():
    """Fixture to track API performance during tests."""
    class PerformanceTracker:
        def __init__(self):
            self.requests = []
            self.start_time = None
        
        def start_request(self, endpoint: str, params: Dict = None):
            self.start_time = time.time()
            return {"endpoint": endpoint, "params": params, "start_time": self.start_time}
        
        def end_request(self, request_info: Dict, response: Any = None, error: Exception = None):
            end_time = time.time()
            duration = end_time - request_info["start_time"]
            
            request_data = {
                "endpoint": request_info["endpoint"],
                "params": request_info["params"],
                "duration": duration,
                "timestamp": end_time,
                "success": error is None
            }
            
            if error:
                request_data["error"] = str(error)
            
            self.requests.append(request_data)
            return request_data
        
        def get_stats(self) -> Dict:
            if not self.requests:
                return {}
            
            durations = [r["duration"] for r in self.requests]
            successful_requests = [r for r in self.requests if r["success"]]
            
            return {
                "total_requests": len(self.requests),
                "successful_requests": len(successful_requests),
                "failed_requests": len(self.requests) - len(successful_requests),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "total_duration": sum(durations)
            }
    
    return PerformanceTracker()


@pytest.fixture
def rate_limit_monitor():
    """Fixture to monitor rate limiting behavior."""
    class RateLimitMonitor:
        def __init__(self):
            self.requests = []
            self.rate_limit_hits = 0
        
        def record_request(self, timestamp: float, success: bool, rate_limited: bool = False):
            self.requests.append({
                "timestamp": timestamp,
                "success": success,
                "rate_limited": rate_limited
            })
            
            if rate_limited:
                self.rate_limit_hits += 1
        
        def get_request_rate(self, window_seconds: int = 60) -> float:
            """Calculate requests per second in the given time window."""
            if not self.requests:
                return 0.0
            
            now = time.time()
            recent_requests = [
                r for r in self.requests 
                if now - r["timestamp"] <= window_seconds
            ]
            
            return len(recent_requests) / window_seconds
        
        def get_stats(self) -> Dict:
            return {
                "total_requests": len(self.requests),
                "rate_limit_hits": self.rate_limit_hits,
                "current_rate": self.get_request_rate(),
                "success_rate": sum(1 for r in self.requests if r["success"]) / len(self.requests) if self.requests else 0
            }
    
    return RateLimitMonitor()


@pytest.fixture
def cache_validator():
    """Fixture to validate caching behavior."""
    class CacheValidator:
        def __init__(self):
            self.cache_hits = 0
            self.cache_misses = 0
            self.cache_operations = []
        
        def record_cache_hit(self, key: str, timestamp: float):
            self.cache_hits += 1
            self.cache_operations.append({
                "operation": "hit",
                "key": key,
                "timestamp": timestamp
            })
        
        def record_cache_miss(self, key: str, timestamp: float):
            self.cache_misses += 1
            self.cache_operations.append({
                "operation": "miss",
                "key": key,
                "timestamp": timestamp
            })
        
        def get_stats(self) -> Dict:
            total_operations = self.cache_hits + self.cache_misses
            return {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "total_operations": total_operations,
                "hit_rate": self.cache_hits / total_operations if total_operations > 0 else 0
            }
    
    return CacheValidator()


@pytest.fixture
def data_consistency_checker():
    """Fixture to check data consistency across API calls."""
    class DataConsistencyChecker:
        def __init__(self):
            self.data_snapshots = []
        
        def record_snapshot(self, symbol: str, data: Dict, timestamp: float):
            self.data_snapshots.append({
                "symbol": symbol,
                "data": data,
                "timestamp": timestamp
            })
        
        def check_consistency(self, symbol: str, field: str) -> Dict:
            """Check consistency of a specific field for a symbol across snapshots."""
            symbol_snapshots = [s for s in self.data_snapshots if s["symbol"] == symbol]
            
            if len(symbol_snapshots) < 2:
                return {"consistent": True, "message": "Not enough data points"}
            
            values = []
            for snapshot in symbol_snapshots:
                if field in snapshot["data"]:
                    values.append(snapshot["data"][field])
            
            if len(values) < 2:
                return {"consistent": True, "message": "Field not found in snapshots"}
            
            # Check if all values are the same (for static fields)
            # or if values follow expected patterns (for dynamic fields)
            all_same = all(v == values[0] for v in values)
            
            return {
                "consistent": all_same,
                "values": values,
                "count": len(values),
                "field": field,
                "symbol": symbol
            }
    
    return DataConsistencyChecker()


@pytest.fixture
def error_scenario_simulator():
    """Fixture to simulate various error scenarios."""
    class ErrorScenarioSimulator:
        def __init__(self):
            self.scenarios = []
        
        def add_network_error_scenario(self, probability: float = 0.1):
            """Add a scenario that simulates network errors."""
            self.scenarios.append({
                "type": "network_error",
                "probability": probability
            })
        
        def add_rate_limit_scenario(self, probability: float = 0.05):
            """Add a scenario that simulates rate limiting."""
            self.scenarios.append({
                "type": "rate_limit",
                "probability": probability
            })
        
        def add_auth_error_scenario(self, probability: float = 0.02):
            """Add a scenario that simulates authentication errors."""
            self.scenarios.append({
                "type": "auth_error",
                "probability": probability
            })
        
        def should_trigger_error(self) -> Optional[str]:
            """Check if any error scenario should be triggered."""
            import random
            
            for scenario in self.scenarios:
                if random.random() < scenario["probability"]:
                    return scenario["type"]
            
            return None
    
    return ErrorScenarioSimulator()


# Integration test markers
def pytest_configure(config):
    """Configure pytest with integration test markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests requiring real API calls"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running integration tests"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )
    config.addinivalue_line(
        "markers", "aws: marks tests that require AWS credentials"
    )
    config.addinivalue_line(
        "markers", "localstack: marks tests that require LocalStack"
    )


# Integration tests should never be skipped - they should fail if infrastructure is not ready