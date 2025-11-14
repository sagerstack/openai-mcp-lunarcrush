# Integration Tests

This directory contains comprehensive integration tests for the LunarCrush API project. These tests validate real-world interactions between all system components including the LunarCrush API, S3 storage, and Lambda function.

## Overview

The integration test suite validates:

- **API Integration**: Real LunarCrush API calls with authentication, rate limiting, and data validation
- **S3 Integration**: Real S3 operations (LocalStack and AWS) with file storage and retrieval
- **Lambda Integration**: Complete Lambda function execution with event processing and response formatting
- **End-to-End Workflows**: Full pipeline testing from API request to S3 storage

## Prerequisites

### Environment Variables

Integration tests require the following environment variables:

```bash
# Required
export ENABLE_INTEGRATION_TESTS=true
export LUNARCRUSH_API_KEY=your_api_key_here
export S3_BUCKET_NAME=your_test_bucket_name

# Optional
export LOCALSTACK_ENDPOINT=http://localhost:4566  # For LocalStack testing
export AWS_DEFAULT_REGION=us-east-1
export LOG_LEVEL=DEBUG
export SYMBOLS_LIST=BTC,ETH,ADA,DOT,LINK
```

### Dependencies

Install integration test dependencies:

```bash
pip install -e .[integration]
```

### LocalStack (Optional)

For local S3 testing, you can use LocalStack:

```bash
# Start LocalStack with S3
docker run -d -p 4566:4566 localstack/localstack

# Create test bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://lunarcrush-test-bucket
```

### AWS Credentials (Optional)

If not using LocalStack, configure AWS credentials:

```bash
aws configure
# Or use IAM roles, environment variables, etc.
```

## Running Tests

### Quick Start

```bash
# Run all integration tests
./tests/integration/run_integration_tests.py

# Or using pytest directly
pytest tests/integration/ -m integration
```

### Advanced Usage

```bash
# Run specific test file
./tests/integration/run_integration_tests.py -- test_api_integration.py

# Run with coverage
./tests/integration/run_integration_tests.py -- --cov=src --cov-report=html

# Run with specific pytest options
./tests/integration/run_integration_tests.py -- -k "test_api" --maxfail=1 -v

# Check prerequisites only
./tests/integration/run_integration_tests.py --check-only

# Setup environment only
./tests/integration/run_integration_tests.py --setup-only
```

## Test Structure

### Test Files

- **`test_api_integration.py`** - Tests real LunarCrush API interactions
- **`test_s3_integration.py`** - Tests S3 storage operations
- **`test_lambda_integration.py`** - Tests Lambda function execution
- **`test_e2e_workflow.py`** - Tests complete end-to-end workflows

### Configuration

- **`conftest.py`** - Integration test fixtures and configuration
- **`test_data_utils.py`** - Test data generation and management utilities
- **`run_integration_tests.py`** - Test runner with environment setup

### Test Data

Test data is generated dynamically using realistic scenarios:

- **Basic Test**: Common symbols (BTC, ETH, ADA)
- **Extended Test**: 10+ symbols for volume testing
- **Edge Cases**: Boundary values and null data
- **Stress Test**: 20+ symbols with extreme values
- **Invalid Symbols**: Non-existent symbols for error handling

## Test Categories

### API Integration Tests (`@pytest.mark.integration`)

- Authentication with real API keys
- Current metrics extraction
- Historical data retrieval
- Percentage change calculations
- Rate limiting behavior
- Retry logic with network failures
- Caching behavior
- Multiple symbol processing
- Error handling
- Data validation
- Concurrent requests

### S3 Integration Tests (`@pytest.mark.aws`)

- Connection and bucket access
- File upload and retrieval
- Archive management
- JSON formatting validation
- Error handling and recovery
- Large data handling
- Concurrent operations
- LocalStack integration

### Lambda Integration Tests

- Complete function execution
- Event processing and validation
- Component integration
- Error propagation
- Performance testing
- Environment validation
- Response formatting
- CORS headers
- Symbol validation

### End-to-End Workflow Tests (`@pytest.mark.slow`)

- Complete API → S3 workflows
- Various symbol combinations
- Data consistency validation
- Performance under load
- Error recovery scenarios
- Time period testing
- Long-running stability

## Acceptance Criteria Coverage

The integration tests validate the following acceptance criteria:

- **AC-1**: Extract current social metrics for specified symbols ✓
- **AC-2**: Retrieve historical time series data for past 24 hours ✓
- **AC-3**: Calculate accurate 24-hour percentage changes ✓
- **AC-4**: Process multiple symbols efficiently within API rate limits ✓
- **AC-5**: Handle missing data gracefully and log validation errors ✓
- **AC-6**: Implement throttling to stay within 500 requests/day limit ✓
- **AC-7**: Implement retry logic with exponential backoff ✓
- **AC-8**: Return cached values if within 5-minute cache window ✓
- **AC-11**: Create properly formatted JSON files in S3 bucket with correct naming ✓

## Performance Benchmarks

### Expected Performance

- **API Response**: < 30 seconds for multiple symbols
- **S3 Storage**: < 10 seconds for typical datasets
- **S3 Retrieval**: < 5 seconds for cached data
- **Lambda Execution**: < 60 seconds total
- **Concurrent Requests**: Handle 5+ parallel requests
- **Rate Limiting**: Stay within 500 requests/day limit

### Stress Testing

- **Large Datasets**: 50+ symbols
- **Extended Duration**: Multiple iterations over time
- **High Concurrency**: 10+ parallel requests
- **Error Recovery**: Graceful degradation under failures

## Troubleshooting

### Common Issues

1. **Tests are skipped**
   - Set `ENABLE_INTEGRATION_TESTS=true`
   - Check `LUNARCRUSH_API_KEY` is valid
   - Verify `S3_BUCKET_NAME` is accessible

2. **Authentication failures**
   - Verify API key is valid and active
   - Check API key permissions
   - Ensure API key hasn't expired

3. **S3 connection issues**
   - Verify AWS credentials are configured
   - Check bucket exists and is accessible
   - Test LocalStack if using local endpoint

4. **Network timeouts**
   - Check internet connectivity
   - Verify firewall settings
   - Try running tests individually

5. **Rate limiting**
   - Wait between test runs
   - Check API quota usage
   - Use test API key if available

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
./tests/integration/run_integration_tests.py -- -v -s
```

### Test Data Issues

Clean up corrupted test data:

```bash
python -c "
from tests.integration.test_data_utils import cleanup_old_test_data
print(f'Cleaned {cleanup_old_test_data(0)} files')
"
```

## Continuous Integration

### GitHub Actions

```yaml
- name: Run Integration Tests
  env:
    ENABLE_INTEGRATION_TESTS: true
    LUNARCRUSH_API_KEY: ${{ secrets.LUNARCRUSH_API_KEY }}
    S3_BUCKET_NAME: ${{ secrets.S3_BUCKET_NAME }}
  run: |
    pip install -e .[integration]
    ./tests/integration/run_integration_tests.py
```

### Local Development

```bash
# Setup environment
export ENABLE_INTEGRATION_TESTS=true
export LUNARCRUSH_API_KEY=your_key
export S3_BUCKET_NAME=your_bucket

# Run tests
./tests/integration/run_integration_tests.py

# Or with LocalStack
export LOCALSTACK_ENDPOINT=http://localhost:4566
./tests/integration/run_integration_tests.py
```

## Contributing

When adding new integration tests:

1. Use appropriate markers (`@pytest.mark.integration`, `@pytest.mark.aws`, etc.)
2. Follow the existing test structure and naming conventions
3. Add proper error handling and test skips for network issues
4. Include performance assertions where applicable
5. Update this README with new test descriptions
6. Add acceptance criteria mapping if applicable

## Security Considerations

- API keys are loaded from environment variables only
- Test data uses realistic but fabricated values
- S3 buckets should be test-only with limited permissions
- LocalStack is recommended for local development
- Never commit credentials to version control