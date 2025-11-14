"""
E2E test utilities and helper functions.

This module provides utility functions and helper classes for E2E testing,
including Docker management, test data generation, performance measurement,
and test result validation.
"""

import json
import time
import subprocess
import threading
import statistics
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone
import requests
import boto3
from botocore.exceptions import ClientError

import docker
from docker.client import DockerClient
from docker.errors import DockerException, APIError


class DockerManager:
    """Utility class for managing Docker containers and environments."""
    
    def __init__(self, compose_file: str = "docker-compose.yml"):
        """Initialize Docker manager.
        
        Args:
            compose_file: Path to docker-compose file
        """
        self.compose_file = compose_file
        self.client = None
        try:
            self.client = docker.from_env()
        except DockerException:
            print("Warning: Docker not available")
    
    def is_docker_available(self) -> bool:
        """Check if Docker is available and running."""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except DockerException:
            return False
    
    def is_docker_compose_available(self) -> bool:
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
    
    def start_services(self, timeout: int = 120) -> bool:
        """Start Docker services using docker-compose.
        
        Args:
            timeout: Timeout in seconds for startup
            
        Returns:
            True if services started successfully, False otherwise
        """
        if not self.is_docker_compose_available():
            print("docker-compose not available")
            return False
        
        try:
            print(f"Starting Docker services with {self.compose_file}...")
            subprocess.run(
                ["docker-compose", "-f", self.compose_file, "up", "-d"],
                check=True,
                timeout=timeout
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to start Docker services: {e}")
            return False
        except subprocess.TimeoutExpired:
            print("Docker services startup timed out")
            return False
    
    def stop_services(self, timeout: int = 60) -> bool:
        """Stop Docker services using docker-compose.
        
        Args:
            timeout: Timeout in seconds for shutdown
            
        Returns:
            True if services stopped successfully, False otherwise
        """
        if not self.is_docker_compose_available():
            print("docker-compose not available")
            return False
        
        try:
            print("Stopping Docker services...")
            subprocess.run(
                ["docker-compose", "-f", self.compose_file, "down", "-v"],
                check=True,
                timeout=timeout
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop Docker services: {e}")
            return False
        except subprocess.TimeoutExpired:
            print("Docker services shutdown timed out")
            return False
    
    def wait_for_service_health(self, service_name: str, max_wait: int = 120) -> bool:
        """Wait for a service to become healthy.
        
        Args:
            service_name: Name of the service to wait for
            max_wait: Maximum wait time in seconds
            
        Returns:
            True if service became healthy, False otherwise
        """
        if not self.client:
            return False
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                container = self.client.containers.get(service_name)
                health = container.attrs.get("State", {}).get("Health", {})
                
                if health.get("Status") == "healthy":
                    return True
                
                time.sleep(5)
            except DockerException:
                time.sleep(5)
        
        return False
    
    def get_container_logs(self, container_name: str, lines: int = 50) -> str:
        """Get logs from a container.
        
        Args:
            container_name: Name of the container
            lines: Number of lines to retrieve
            
        Returns:
            Container logs as string
        """
        if not self.client:
            return ""
        
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=lines)
            return logs.decode("utf-8")
        except DockerException:
            return ""
    
    def get_container_stats(self, container_name: str) -> Dict[str, Any]:
        """Get resource usage statistics for a container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Dictionary with resource statistics
        """
        if not self.client:
            return {}
        
        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # Extract relevant statistics
            memory_stats = stats.get("memory_stats", {})
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})
            
            return {
                "memory_usage": memory_stats.get("usage", 0),
                "memory_limit": memory_stats.get("limit", 0),
                "memory_usage_percent": (
                    (memory_stats.get("usage", 0) / memory_stats.get("limit", 1)) * 100
                    if memory_stats.get("limit", 0) > 0 else 0
                ),
                "cpu_usage": cpu_stats.get("cpu_usage", {}).get("total_usage", 0),
                "system_cpu_usage": cpu_stats.get("system_cpu_usage", 0),
                "precpu_usage": precpu_stats.get("cpu_usage", {}).get("total_usage", 0),
                "pre_system_cpu_usage": precpu_stats.get("system_cpu_usage", 0)
            }
        except DockerException:
            return {}


class TestDataGenerator:
    """Utility class for generating test data for E2E tests."""
    
    @staticmethod
    def generate_symbols(count: int, prefix: str = "TEST") -> List[str]:
        """Generate test cryptocurrency symbols.
        
        Args:
            count: Number of symbols to generate
            prefix: Prefix for symbol names
            
        Returns:
            List of generated symbols
        """
        return [f"{prefix}{i:03d}" for i in range(1, count + 1)]
    
    @staticmethod
    def generate_real_symbols() -> List[str]:
        """Get list of real cryptocurrency symbols for testing.
        
        Returns:
            List of real cryptocurrency symbols
        """
        return [
            "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "MATIC", "AVAX",
            "LINK", "UNI", "LTC", "ATOM", "XLM", "NEAR", "ALGO", "VET", "FTM", "ICP",
            "HBAR", "FIL", "TRX", "ETC", "XMR", "EGLD", "AAVE", "MKR", "COMP", "SUSHI"
        ]
    
    @staticmethod
    def generate_lambda_event(symbols: List[str], parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a Lambda event payload.
        
        Args:
            symbols: List of cryptocurrency symbols
            parameters: Optional parameters dictionary
            
        Returns:
            Lambda event payload
        """
        return {
            "symbols": symbols,
            "parameters": parameters or {}
        }
    
    @staticmethod
    def generate_large_symbol_set(size: int = 50) -> List[str]:
        """Generate a large set of symbols for performance testing.
        
        Args:
            size: Number of symbols to generate
            
        Returns:
            List of symbols
        """
        real_symbols = TestDataGenerator.generate_real_symbols()
        generated_symbols = TestDataGenerator.generate_symbols(size - len(real_symbols), "PERF")
        
        return real_symbols + generated_symbols[:size - len(real_symbols)]


class PerformanceMeasurer:
    """Utility class for measuring performance during tests."""
    
    def __init__(self):
        """Initialize performance measurer."""
        self.measurements = []
        self.start_times = {}
    
    def start_measurement(self, operation_id: str) -> None:
        """Start measuring an operation.
        
        Args:
            operation_id: Unique identifier for the operation
        """
        self.start_times[operation_id] = time.time()
    
    def end_measurement(self, operation_id: str, success: bool = True, error: Optional[str] = None) -> Dict[str, Any]:
        """End measuring an operation.
        
        Args:
            operation_id: Unique identifier for the operation
            success: Whether the operation was successful
            error: Error message if operation failed
            
        Returns:
            Measurement result
        """
        if operation_id not in self.start_times:
            return {"error": "Operation not started"}
        
        start_time = self.start_times.pop(operation_id)
        end_time = time.time()
        duration = end_time - start_time
        
        measurement = {
            "operation_id": operation_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "success": success,
            "timestamp": end_time
        }
        
        if error:
            measurement["error"] = error
        
        self.measurements.append(measurement)
        return measurement
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics.
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.measurements:
            return {}
        
        durations = [m["duration"] for m in self.measurements]
        successful_measurements = [m for m in self.measurements if m["success"]]
        failed_measurements = [m for m in self.measurements if not m["success"]]
        
        stats = {
            "total_operations": len(self.measurements),
            "successful_operations": len(successful_measurements),
            "failed_operations": len(failed_measurements),
            "success_rate": len(successful_measurements) / len(self.measurements),
            "total_duration": sum(durations),
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations)
        }
        
        if len(durations) > 1:
            stats["duration_stddev"] = statistics.stdev(durations)
            stats["duration_median"] = statistics.median(durations)
        
        if successful_measurements:
            successful_durations = [m["duration"] for m in successful_measurements]
            stats["avg_successful_duration"] = statistics.mean(successful_durations)
            stats["min_successful_duration"] = min(successful_durations)
            stats["max_successful_duration"] = max(successful_durations)
        
        if failed_measurements:
            failed_durations = [m["duration"] for m in failed_measurements]
            stats["avg_failed_duration"] = statistics.mean(failed_durations)
            stats["min_failed_duration"] = min(failed_durations)
            stats["max_failed_duration"] = max(failed_durations)
        
        return stats
    
    def reset(self) -> None:
        """Reset all measurements."""
        self.measurements = []
        self.start_times = {}


class ResponseValidator:
    """Utility class for validating Lambda responses."""
    
    @staticmethod
    def validate_lambda_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Lambda response structure.
        
        Args:
            response: Lambda response dictionary
            
        Returns:
            Validation result with errors if any
        """
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
        if response.get("statusCode") not in [200, 400, 429, 500, 502, 503]:
            errors.append(f"Unexpected status code: {response.get('statusCode')}")
        
        # Parse and validate body
        try:
            body = json.loads(response.get("body", "{}"))
            
            if not isinstance(body, dict):
                errors.append("Body must be a JSON object")
            else:
                # Check for success flag
                if "success" not in body:
                    errors.append("Missing 'success' field in response body")
                
                # Check for data field if successful
                if body.get("success") and "data" not in body:
                    errors.append("Missing 'data' field in successful response")
                
                # Check for error field if failed
                if not body.get("success") and "error" not in body:
                    errors.append("Missing 'error' field in failed response")
        
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in response body: {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_metrics_structure(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate metrics structure.
        
        Args:
            metrics: List of metrics dictionaries
            
        Returns:
            Validation result with errors if any
        """
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


class S3TestHelper:
    """Utility class for S3 testing operations."""
    
    def __init__(self, endpoint_url: Optional[str] = None, aws_region: str = "us-east-1"):
        """Initialize S3 test helper.
        
        Args:
            endpoint_url: S3 endpoint URL (for LocalStack)
            aws_region: AWS region
        """
        self.endpoint_url = endpoint_url
        self.aws_region = aws_region
        self.client = None
        
        try:
            s3_config = {
                "region_name": aws_region,
                "aws_access_key_id": "test",
                "aws_secret_access_key": "test"
            }
            
            if endpoint_url:
                s3_config["endpoint_url"] = endpoint_url
            
            self.client = boto3.client("s3", **s3_config)
        except Exception as e:
            print(f"Failed to initialize S3 client: {e}")
    
    def create_bucket(self, bucket_name: str) -> bool:
        """Create an S3 bucket.
        
        Args:
            bucket_name: Name of the bucket to create
            
        Returns:
            True if bucket created successfully, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.create_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyExists":
                return True
            print(f"Failed to create bucket: {e}")
            return False
    
    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if a bucket exists.
        
        Args:
            bucket_name: Name of the bucket
            
        Returns:
            True if bucket exists, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            return False
    
    def put_object(self, bucket_name: str, key: str, data: Union[str, bytes], content_type: str = "application/json") -> bool:
        """Put an object in S3.
        
        Args:
            bucket_name: Name of the bucket
            key: Object key
            data: Object data
            content_type: Content type of the object
            
        Returns:
            True if object put successfully, False otherwise
        """
        if not self.client:
            return False
        
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")
            
            self.client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=data,
                ContentType=content_type
            )
            return True
        except ClientError as e:
            print(f"Failed to put object: {e}")
            return False
    
    def get_object(self, bucket_name: str, key: str) -> Optional[str]:
        """Get an object from S3.
        
        Args:
            bucket_name: Name of the bucket
            key: Object key
            
        Returns:
            Object data as string, or None if not found
        """
        if not self.client:
            return None
        
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=key)
            return response["Body"].read().decode("utf-8")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            print(f"Failed to get object: {e}")
            return None
    
    def list_objects(self, bucket_name: str, prefix: str = "") -> List[Dict[str, Any]]:
        """List objects in a bucket.
        
        Args:
            bucket_name: Name of the bucket
            prefix: Object key prefix
            
        Returns:
            List of object information
        """
        if not self.client:
            return []
        
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            return response.get("Contents", [])
        except ClientError as e:
            print(f"Failed to list objects: {e}")
            return []
    
    def delete_object(self, bucket_name: str, key: str) -> bool:
        """Delete an object from S3.
        
        Args:
            bucket_name: Name of the bucket
            key: Object key
            
        Returns:
            True if object deleted successfully, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.delete_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError as e:
            print(f"Failed to delete object: {e}")
            return False


class HealthChecker:
    """Utility class for checking service health."""
    
    @staticmethod
    def check_http_health(url: str, timeout: int = 10) -> bool:
        """Check HTTP service health.
        
        Args:
            url: URL to check
            timeout: Request timeout in seconds
            
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    @staticmethod
    def check_lambda_health(lambda_endpoint: str, timeout: int = 10) -> bool:
        """Check Lambda function health.
        
        Args:
            lambda_endpoint: Lambda endpoint URL
            timeout: Request timeout in seconds
            
        Returns:
            True if Lambda is healthy, False otherwise
        """
        try:
            url = f"{lambda_endpoint}/2015-03-31/functions/function/invocations"
            response = requests.post(
                url,
                json={"symbols": ["BTC"]},
                timeout=timeout
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    @staticmethod
    def check_s3_health(s3_endpoint: str, timeout: int = 10) -> bool:
        """Check S3 service health.
        
        Args:
            s3_endpoint: S3 endpoint URL
            timeout: Request timeout in seconds
            
        Returns:
            True if S3 is healthy, False otherwise
        """
        try:
            health_url = f"{s3_endpoint}/health"
            response = requests.get(health_url, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False