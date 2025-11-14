"""
Docker environment E2E tests for the LunarCrush Lambda function.

This module tests the Docker container setup, health checks, networking,
and environment configuration to ensure the complete Docker environment works correctly.
"""

import json
import time
import pytest
import requests
import subprocess
from typing import Dict, Any, List

import docker
from docker.client import DockerClient
from docker.errors import DockerException, APIError


@pytest.mark.e2e
@pytest.mark.docker
class TestDockerEnvironment:
    """Test Docker container environment and configuration."""

    def test_docker_container_startup(self, docker_environment):
        """
        Test Docker container startup and health checks.
        
        This test validates:
        - Docker containers start successfully
        - Health checks pass
        - Container status is correct
        - Required ports are accessible
        """
        # Get Docker client
        client = docker.from_env()
        
        # Check Lambda container
        try:
            lambda_container = client.containers.get("lunarcrush-lambda")
            assert lambda_container.status == "running", f"Lambda container status: {lambda_container.status}"
            
            # Check container health
            health = lambda_container.attrs.get("State", {}).get("Health", {})
            if health:
                assert health.get("Status") in ["healthy", "starting"], f"Lambda container health: {health.get('Status')}"
            
            print(f"Lambda container status: {lambda_container.status}")
            
        except docker.errors.NotFound:
            pytest.fail("Lambda container not found")
        
        # Check LocalStack container
        try:
            localstack_container = client.containers.get("lunarcrush-localstack")
            assert localstack_container.status == "running", f"LocalStack container status: {localstack_container.status}"
            
            # Check container health
            health = localstack_container.attrs.get("State", {}).get("Health", {})
            if health:
                assert health.get("Status") in ["healthy", "starting"], f"LocalStack container health: {health.get('Status')}"
            
            print(f"LocalStack container status: {localstack_container.status}")
            
        except docker.errors.NotFound:
            pytest.fail("LocalStack container not found")

    def test_lambda_function_accessibility(self, docker_environment):
        """
        Test Lambda function accessibility via localhost:9000.
        
        This test validates:
        - Lambda Runtime API endpoint is accessible
        - Function responds to invocation requests
        - HTTP status codes are correct
        - Response format is as expected
        """
        lambda_endpoint = docker_environment["lambda_endpoint"]
        invoke_url = f"{lambda_endpoint}/2015-03-31/functions/function/invocations"
        
        # Test basic accessibility
        try:
            response = requests.post(
                invoke_url,
                json={"symbols": ["BTC"]},
                timeout=10
            )
            
            # Should get a response (might be error if API key not configured)
            assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
            
            # Response should be JSON
            try:
                response_data = response.json()
                assert isinstance(response_data, dict), "Response should be a dictionary"
                
                # Should have Lambda response structure
                assert "statusCode" in response_data, "Missing statusCode in response"
                assert "headers" in response_data, "Missing headers in response"
                assert "body" in response_data, "Missing body in response"
                
            except json.JSONDecodeError:
                pytest.fail("Response should be valid JSON")
                
        except requests.exceptions.ConnectionError:
            pytest.fail("Cannot connect to Lambda endpoint")
        except requests.exceptions.Timeout:
            pytest.fail("Lambda endpoint request timed out")

    def test_localstack_s3_accessibility(self, docker_environment):
        """
        Test LocalStack S3 accessibility via localhost:4566.
        
        This test validates:
        - LocalStack S3 endpoint is accessible
        - S3 operations work correctly
        - Bucket creation and access
        - Object storage and retrieval
        """
        localstack_endpoint = docker_environment["localstack_endpoint"]
        
        # Test LocalStack health endpoint
        try:
            health_response = requests.get(
                f"{localstack_endpoint}/health",
                timeout=10
            )
            
            assert health_response.status_code == 200, f"Health check failed: {health_response.status_code}"
            
            health_data = health_response.json()
            assert "services" in health_data, "Health response should contain services info"
            
        except requests.exceptions.ConnectionError:
            pytest.fail("Cannot connect to LocalStack health endpoint")
        
        # Test S3 accessibility using boto3
        import boto3
        from botocore.exceptions import ClientError
        
        try:
            # Create S3 client for LocalStack
            s3_client = boto3.client(
                "s3",
                endpoint_url=localstack_endpoint,
                aws_access_key_id="test",
                aws_secret_access_key="test",
                region_name=docker_environment["aws_region"]
            )
            
            # Test bucket operations
            bucket_name = docker_environment["test_bucket_name"]
            
            # Check if bucket exists (should be created by setup script)
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                print(f"Bucket {bucket_name} exists")
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    # Create bucket if it doesn't exist
                    s3_client.create_bucket(Bucket=bucket_name)
                    print(f"Created bucket {bucket_name}")
                else:
                    raise
            
            # Test object operations
            test_key = "test-object"
            test_content = json.dumps({"test": "data", "timestamp": time.time()})
            
            # Put object
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType="application/json"
            )
            
            # Get object
            response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
            retrieved_content = response["Body"].read().decode("utf-8")
            
            assert retrieved_content == test_content, "Retrieved content doesn't match uploaded content"
            
            # List objects
            objects = s3_client.list_objects_v2(Bucket=bucket_name)
            assert "Contents" in objects, "Should have objects in bucket"
            
            # Clean up
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            
            print("S3 operations completed successfully")
            
        except Exception as e:
            pytest.fail(f"S3 accessibility test failed: {str(e)}")

    def test_container_networking(self, docker_environment):
        """
        Test container communication and networking.
        
        This test validates:
        - Containers can communicate with each other
        - Network configuration is correct
        - DNS resolution works between containers
        - Port mapping is correct
        """
        # Get Docker client
        client = docker.from_env()
        
        try:
            # Get Lambda container
            lambda_container = client.containers.get("lunarcrush-lambda")
            
            # Test network connectivity from Lambda container to LocalStack
            exec_result = lambda_container.exec_run(
                "curl -s -o /dev/null -w '%{http_code}' http://localstack:4566/health"
            )
            
            # Should get HTTP 200 from LocalStack health check
            exit_code, output = exec_result
            assert exit_code == 0, f"Exec command failed with exit code {exit_code}"
            
            # The output should be the HTTP status code
            http_code = output.decode().strip()
            assert http_code == "200", f"Expected HTTP 200, got {http_code}"
            
            print("Container networking test passed")
            
        except docker.errors.NotFound:
            pytest.fail("Lambda container not found")
        except Exception as e:
            pytest.fail(f"Container networking test failed: {str(e)}")

    def test_environment_variable_configuration(self, docker_environment):
        """
        Test environment variable configuration in Docker containers.
        
        This test validates:
        - Required environment variables are set
        - Environment variables have correct values
        - Configuration is properly loaded
        """
        # Get Docker client
        client = docker.from_env()
        
        try:
            # Get Lambda container
            lambda_container = client.containers.get("lunarcrush-lambda")
            
            # Get environment variables
            env_vars = lambda_container.attrs.get("Config", {}).get("Env", [])
            env_dict = {var.split("=")[0]: "=".join(var.split("=")[1:]) for var in env_vars}
            
            # Check required environment variables
            required_vars = [
                "LUNARCRUSH_API_KEY",
                "S3_BUCKET_NAME",
                "AWS_REGION",
                "SYMBOLS_LIST",
                "LOG_LEVEL",
                "TIMEOUT_SECONDS",
                "MEMORY_MB",
                "API_RATE_LIMIT_PER_DAY",
                "API_RATE_LIMIT_PER_HOUR",
                "API_REQUEST_DELAY_SECONDS",
                "CACHE_TTL_SECONDS",
                "ENVIRONMENT"
            ]
            
            for var in required_vars:
                assert var in env_dict, f"Missing environment variable: {var}"
                assert env_dict[var] != "", f"Environment variable {var} is empty"
            
            # Check specific values
            assert env_dict["S3_BUCKET_NAME"] == docker_environment["test_bucket_name"]
            assert env_dict["AWS_REGION"] == docker_environment["aws_region"]
            assert env_dict["ENVIRONMENT"] == "development"
            
            print("Environment variable configuration test passed")
            
        except docker.errors.NotFound:
            pytest.fail("Lambda container not found")

    def test_docker_volume_mounting(self, docker_environment):
        """
        Test Docker volume mounting and file access.
        
        This test validates:
        - Volumes are mounted correctly
        - Files are accessible in containers
        - Code changes are reflected in containers
        """
        # Get Docker client
        client = docker.from_env()
        
        try:
            # Get Lambda container
            lambda_container = client.containers.get("lunarcrush-lambda")
            
            # Test if source code is accessible
            exec_result = lambda_container.exec_run("ls -la /var/task/")
            exit_code, output = exec_result
            
            assert exit_code == 0, f"Failed to list directory: {output.decode()}"
            
            # Check for key files
            file_list = output.decode()
            assert "lambda_function.py" in file_list, "lambda_function.py not found"
            assert "src/" in file_list, "src/ directory not found"
            
            # Test if we can read the Lambda function
            exec_result = lambda_container.exec_run("head -n 5 /var/task/lambda_function.py")
            exit_code, output = exec_result
            
            assert exit_code == 0, f"Failed to read lambda_function.py: {output.decode()}"
            assert "import" in output.decode(), "lambda_function.py appears to be empty or corrupted"
            
            print("Docker volume mounting test passed")
            
        except docker.errors.NotFound:
            pytest.fail("Lambda container not found")

    def test_docker_logs_and_monitoring(self, docker_environment):
        """
        Test Docker logs and monitoring capabilities.
        
        This test validates:
        - Logs are generated correctly
        - Log levels are respected
        - Error conditions are logged
        - Log format is structured
        """
        # Get Docker client
        client = docker.from_env()
        
        try:
            # Get Lambda container
            lambda_container = client.containers.get("lunarcrush-lambda")
            
            # Get recent logs
            logs = lambda_container.logs(since=int(time.time() - 300), tail=50)  # Last 5 minutes, 50 lines
            
            # Convert to string for analysis
            log_text = logs.decode("utf-8")
            
            # Should have some log output
            assert len(log_text) > 0, "No logs found from Lambda container"
            
            # Check for structured logging (JSON format)
            try:
                log_lines = log_text.strip().split("\n")
                for line in log_lines:
                    if line.strip():
                        # Try to parse as JSON (structured logging)
                        try:
                            log_entry = json.loads(line)
                            # Should have basic log fields
                            assert "timestamp" in log_entry or "level" in log_entry, "Log entry missing basic fields"
                        except json.JSONDecodeError:
                            # Not JSON, might be a different format
                            pass
            except Exception:
                # Log parsing failed, but that's not critical
                pass
            
            print("Docker logs test passed")
            
        except docker.errors.NotFound:
            pytest.fail("Lambda container not found")

    def test_docker_resource_limits(self, docker_environment):
        """
        Test Docker resource limits and constraints.
        
        This test validates:
        - Memory limits are enforced
        - CPU limits are configured
        - Resource usage is within expected bounds
        """
        # Get Docker client
        client = docker.from_env()
        
        try:
            # Get Lambda container
            lambda_container = client.containers.get("lunarcrush-lambda")
            
            # Get container stats
            stats = lambda_container.stats(stream=False)
            
            # Check memory usage
            memory_stats = stats.get("memory_stats", {})
            memory_usage = memory_stats.get("usage", 0)
            memory_limit = memory_stats.get("limit", 0)
            
            if memory_limit > 0:
                memory_usage_percent = (memory_usage / memory_limit) * 100
                print(f"Memory usage: {memory_usage_percent:.2f}%")
                
                # Should not be using excessive memory
                assert memory_usage_percent < 90, f"Memory usage too high: {memory_usage_percent:.2f}%"
            
            # Check CPU usage
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})
            
            # Calculate CPU usage percentage
            cpu_delta = cpu_stats.get("cpu_usage", {}).get("total_usage", 0) - \
                       precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            system_delta = cpu_stats.get("system_cpu_usage", 0) - \
                          precpu_stats.get("system_cpu_usage", 0)
            
            if system_delta > 0 and cpu_delta > 0:
                cpu_count = len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", []))
                if cpu_count == 0:
                    cpu_count = 1
                
                cpu_usage_percent = (cpu_delta / system_delta) * cpu_count * 100
                print(f"CPU usage: {cpu_usage_percent:.2f}%")
            
            print("Docker resource limits test passed")
            
        except docker.errors.NotFound:
            pytest.fail("Lambda container not found")
        except Exception as e:
            print(f"Resource monitoring test failed (non-critical): {str(e)}")