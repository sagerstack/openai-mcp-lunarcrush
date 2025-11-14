# End-to-End (E2E) Tests

This directory contains comprehensive end-to-end tests for the LunarCrush Lambda function, validating the complete workflow from API calls through data processing to S3 storage.

## Overview

The E2E test suite validates all acceptance criteria and real-world usage scenarios, including:

- Complete workflow validation (Lambda → API → Processing → S3)
- Docker environment functionality
- Performance requirements and scalability
- Error handling and recovery scenarios
- Integration with LocalStack for S3 testing

## Test Structure

```
tests/e2e/
├── __init__.py                 # E2E test package initialization
├── conftest.py                 # E2E test configuration and fixtures
├── utils.py                    # E2E test utilities and helper classes
├── test_complete_workflow.py     # Complete workflow E2E tests
├── test_docker_environment.py   # Docker environment E2E tests
├── test_performance_scenarios.py # Performance scenario E2E tests
├── test_error_scenarios.py      # Error scenario E2E tests
└── README.md                   # This documentation
```

## Prerequisites

### Environment Setup

1. **Docker and Docker Compose**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Python Dependencies**
   ```bash
   # Install E2E test dependencies
   pip install -e ".[e2e]"
   ```

3. **Environment Variables**
   ```bash
   # Required for E2E tests
   export ENABLE_E2E_TESTS=true
   export LUNARCRUSH_API_KEY=your_api_key_here
   
   # Optional: Custom configuration
   export S3_BUCKET_NAME=custom-test-bucket
   export AWS_DEFAULT_REGION=us-east-1
   ```

### Port Availability

Ensure the following ports are available:
- `9000` - Lambda Runtime API endpoint
- `4566` - LocalStack S3 endpoint

## Running E2E Tests

### Basic E2E Test Execution

```bash
# Run all E2E tests
pytest tests/e2e/ -m e2e

# Run with verbose output
pytest tests/e2e/ -m e2e -v

# Run with coverage
pytest tests/e2e/ -m e2e --cov=src --cov-report=html
```

### Running Specific Test Categories

```bash
# Run only complete workflow tests
pytest tests/e2e/test_complete_workflow.py -m e2e

# Run only Docker environment tests
pytest tests/e2e/test_docker_environment.py -m e2e -m docker

# Run only performance tests
pytest tests/e2e/test_performance_scenarios.py -m e2e -m performance

# Run only error scenario tests
pytest tests/e2e/test_error_scenarios.py -m e2e
```

### Running with Custom Configuration

```bash
# Run with custom timeout
pytest tests/e2e/ -m e2e --timeout=300

# Run with parallel execution
pytest tests/e2e/ -m e2e -n 4

# Run with specific markers
pytest tests/e2e/ -m "e2e and not slow"
```

## Test Categories

### 1. Complete Workflow Tests (`test_complete_workflow.py`)

Validates the end-to-end workflow from Lambda invocation to S3 storage:

- **AC-1**: Basic workflow with two symbols (BTC, ETH)
- **AC-4**: Performance with 50 symbols within 30 seconds
- **AC-11**: S3 storage integration
- Real API integration testing
- Custom parameter handling
- Error handling for invalid inputs

### 2. Docker Environment Tests (`test_docker_environment.py`)

Validates Docker container setup and configuration:

- Container startup and health checks
- Lambda function accessibility
- LocalStack S3 accessibility
- Container networking
- Environment variable configuration
- Volume mounting and file access
- Docker logs and monitoring
- Resource limits and constraints

### 3. Performance Scenario Tests (`test_performance_scenarios.py`)

Validates performance requirements and scalability:

- **AC-4**: Processing 50 symbols within 30 seconds
- **AC-10**: Lambda execution within timeout and memory limits
- Concurrent request handling
- API rate limiting under load
- Cache performance under repeated requests
- Performance scaling with varying symbol counts

### 4. Error Scenario Tests (`test_error_scenarios.py`)

Validates error handling and recovery mechanisms:

- **AC-5**: Handling invalid symbols and missing data
- **AC-6**: API rate limiting and throttling
- **AC-7**: Retry logic with simulated failures
- Graceful degradation when services unavailable
- Error logging and monitoring
- Timeout handling
- Memory pressure handling

## Acceptance Criteria Coverage

| AC | Description | Test Coverage |
|----|-------------|---------------|
| AC-1 | Extract social metrics for cryptocurrency symbols | `test_complete_workflow.py::TestCompleteWorkflow::test_ac1_basic_workflow_with_two_symbols` |
| AC-4 | Process 50 symbols within 30 seconds | `test_performance_scenarios.py::TestPerformanceScenarios::test_ac4_processing_50_symbols_within_30_seconds` |
| AC-5 | Handle invalid symbols and missing data | `test_error_scenarios.py::TestErrorScenarios::test_ac5_handling_invalid_symbols_and_missing_data` |
| AC-6 | API rate limiting and throttling | `test_error_scenarios.py::TestErrorScenarios::test_ac6_api_rate_limiting_and_throttling` |
| AC-7 | Retry logic with simulated failures | `test_error_scenarios.py::TestErrorScenarios::test_ac7_retry_logic_with_simulated_failures` |
| AC-10 | Lambda execution within timeout and memory limits | `test_performance_scenarios.py::TestPerformanceScenarios::test_lambda_execution_within_timeout_and_memory_limits` |
| AC-11 | S3 storage integration | `test_complete_workflow.py::TestCompleteWorkflow::test_ac11_s3_storage_integration` |

## Test Configuration

### E2E Test Configuration

The E2E tests use the following configuration (defined in `conftest.py`):

```python
E2E_TEST_CONFIG = {
    "docker_compose_file": "docker-compose.yml",
    "lambda_endpoint": "http://localhost:9000",
    "localstack_endpoint": "http://localhost:4566",
    "test_bucket_name": "local-test-bucket",
    "aws_region": "us-east-1",
    "test_symbols": ["BTC", "ETH", "ADA", "DOT", "LINK"],
    "large_symbol_set": [f"BTC{i:02d}" for i in range(1, 51)],
    "startup_timeout": 120,  # seconds
    "request_timeout": 30,   # seconds
    "performance_threshold": 30,  # seconds for 50 symbols
    "health_check_interval": 5,  # seconds
    "max_retries": 3,
    "retry_delay": 2,  # seconds
}
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|-----------|---------|-------------|
| `ENABLE_E2E_TESTS` | Yes | `false` | Enable E2E tests |
| `LUNARCRUSH_API_KEY` | Yes | - | LunarCrush API key |
| `S3_BUCKET_NAME` | No | `local-test-bucket` | S3 bucket name for testing |
| `AWS_DEFAULT_REGION` | No | `us-east-1` | AWS region |
| `LOCALSTACK_ENDPOINT` | No | `http://localhost:4566` | LocalStack endpoint |

## Test Utilities

### DockerManager

Manages Docker containers and environments:

```python
from tests.e2e.utils import DockerManager

docker_manager = DockerManager()
docker_manager.start_services()
docker_manager.stop_services()
```

### TestDataGenerator

Generates test data for E2E scenarios:

```python
from tests.e2e.utils import TestDataGenerator

# Generate test symbols
symbols = TestDataGenerator.generate_symbols(50, "TEST")
real_symbols = TestDataGenerator.generate_real_symbols()

# Generate Lambda event
event = TestDataGenerator.generate_lambda_event(symbols)
```

### PerformanceMeasurer

Measures performance during tests:

```python
from tests.e2e.utils import PerformanceMeasurer

measurer = PerformanceMeasurer()
measurer.start_measurement("test_operation")
# ... perform operation ...
result = measurer.end_measurement("test_operation", success=True)
stats = measurer.get_statistics()
```

### ResponseValidator

Validates Lambda response structure:

```python
from tests.e2e.utils import ResponseValidator

validator = ResponseValidator()
result = validator.validate_lambda_response(response)
if not result["valid"]:
    print("Validation errors:", result["errors"])
```

### S3TestHelper

Performs S3 operations for testing:

```python
from tests.e2e.utils import S3TestHelper

s3_helper = S3TestHelper(endpoint_url="http://localhost:4566")
s3_helper.create_bucket("test-bucket")
s3_helper.put_object("test-bucket", "test.json", '{"test": "data"}')
```

## Troubleshooting

### Common Issues

1. **Docker Not Available**
   ```
   Error: Docker is not available or not running
   ```
   **Solution**: Install and start Docker, ensure user has permissions

2. **Ports Already in Use**
   ```
   Error: Port 9000 is already in use
   ```
   **Solution**: Stop other services using ports 9000 and 4566

3. **API Key Missing**
   ```
   Error: Valid API key not found
   ```
   **Solution**: Set `LUNARCRUSH_API_KEY` environment variable

4. **Tests Time Out**
   ```
   Error: Services did not become ready within timeout period
   ```
   **Solution**: Check Docker logs, increase startup timeout

5. **Memory Issues**
   ```
   Error: Memory usage too high
   ```
   **Solution**: Close other applications, increase available memory

### Debug Mode

Run tests with debug output:

```bash
# Enable debug logging
pytest tests/e2e/ -m e2e -v -s --log-cli-level=DEBUG

# Run with pdb debugger
pytest tests/e2e/ -m e2e --pdb
```

### Manual Testing

For manual testing outside of pytest:

```bash
# Start Docker environment
docker-compose up -d

# Test Lambda function
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"symbols": ["BTC", "ETH"]}'

# Test LocalStack S3
aws --endpoint-url=http://localhost:4566 s3 ls s3://local-test-bucket/

# Stop Docker environment
docker-compose down -v
```

## Performance Benchmarks

### Expected Performance

| Metric | Expected | Notes |
|---------|----------|--------|
| 50 symbols processing time | ≤ 30 seconds | AC-4 requirement |
| Lambda execution time | ≤ 60 seconds | Well under Lambda timeout |
| Memory usage | ≤ 512 MB | Docker memory limit |
| Concurrent requests | ≥ 80% success rate | Under moderate load |
| Cache hit performance | Faster than cache miss | When cache is populated |

### Performance Monitoring

Performance is automatically measured during tests and reported in:

- Individual test measurements
- Aggregate statistics
- Resource usage metrics
- Success rates and error rates

## Continuous Integration

### CI/CD Integration

For CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run E2E Tests
  run: |
    docker-compose up -d
    pytest tests/e2e/ -m e2e --junitxml=e2e-results.xml
    docker-compose down -v
  env:
    ENABLE_E2E_TESTS: true
    LUNARCRUSH_API_KEY: ${{ secrets.LUNARCRUSH_API_KEY }}
```

### Test Reports

Generate test reports:

```bash
# JUnit XML for CI systems
pytest tests/e2e/ -m e2e --junitxml=e2e-results.xml

# HTML coverage report
pytest tests/e2e/ -m e2e --cov=src --cov-report=html

# Performance report
pytest tests/e2e/ -m performance --html=e2e-performance.html
```

## Contributing

When adding new E2E tests:

1. Follow the existing test structure and naming conventions
2. Use appropriate markers (`@pytest.mark.e2e`, `@pytest.mark.performance`, etc.)
3. Include comprehensive validation and error handling
4. Add documentation for new test scenarios
5. Update this README file with new test coverage

## Support

For issues with E2E tests:

1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Verify environment variables are set correctly
4. Ensure all prerequisites are installed
5. Check for port conflicts with other services