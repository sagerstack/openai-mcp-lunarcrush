# LunarCrush OpenAI MCP Execution Guide

This comprehensive guide covers how to run unit tests, integration tests, e2e tests, and execute the application in Docker.

## Table of Contents

1. [Prerequisites Setup](#prerequisites-setup)
2. [Unit Tests Execution](#unit-tests-execution)
3. [Integration Tests Execution](#integration-tests-execution)
4. [E2E Tests Execution](#e2e-tests-execution)
5. [Docker Application Execution](#docker-application-execution)
6. [Troubleshooting Section](#troubleshooting-section)
7. [Quick Reference Commands](#quick-reference-commands)

---

## Prerequisites Setup

### Environment Variables

Create a `.env.local` file in the project root with the following configuration:

```bash
# Copy the example file
cp .env.example .env.local
```

Edit `.env.local` with your actual values:

```bash
# Required for all tests
LUNARCRUSH_API_KEY=<your_lunarcrush_api_key_here>
S3_BUCKET_NAME=<your_s3_bucket_name_here>

# AWS Configuration (for integration tests with real AWS)
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1
# AWS_ACCESS_KEY_ID=<your_aws_access_key>
# AWS_SECRET_ACCESS_KEY=<your_aws_secret_key>

# Lambda Configuration
SYMBOLS_LIST=BTC,ETH,ADA,DOT,LINK
LOG_LEVEL=INFO
TIMEOUT_SECONDS=300
MEMORY_MB=512

# Rate Limiting Configuration
API_RATE_LIMIT_PER_DAY=500
API_RATE_LIMIT_PER_HOUR=21
API_REQUEST_DELAY_SECONDS=2

# Cache Configuration
CACHE_TTL_SECONDS=300

# Development/Testing Configuration
ENVIRONMENT=development
DEBUG=false

# LocalStack Configuration (for local testing)
LOCALSTACK_ENDPOINT=http://localhost:4566
S3_ENDPOINT_URL=http://localhost:4566
```

### API Key Configuration

1. **LunarCrush API Key**:
   - Sign up at [LunarCrush](https://lunarcrush.com/)
   - Navigate to API section and generate an API key
   - Add it to your `.env.local` file
   - **Note**: Free tier has rate limits (500 requests/day, 21 requests/hour)

2. **AWS Credentials** (optional for LocalStack):
   - For LocalStack testing, you can use test credentials:
     ```bash
     AWS_ACCESS_KEY_ID=test
     AWS_SECRET_ACCESS_KEY=test
     ```
   - For real AWS S3 integration, configure proper IAM credentials

### Docker and Docker Compose Installation

#### macOS (using Homebrew):
```bash
# Install Docker Desktop
brew install --cask docker

# Or install Docker Engine and Docker Compose separately
brew install docker docker-compose
```

#### Linux (Ubuntu/Debian):
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Windows:
- Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### Python Dependencies Installation

```bash
# Install base dependencies
poetry install

# Install test dependencies
poetry install --with test

# Install integration test dependencies
poetry install --with integration

# Install e2e test dependencies
poetry install --with e2e

# Or install all at once
poetry install --with test,integration,e2e
```

**Time Estimate**: 2-5 minutes for dependency installation

---

## Unit Tests Execution

Unit tests use mocks and do not require external services or API keys.

### Run All Unit Tests

```bash
# Run all unit tests
poetry run pytest -m "unit" tests/

# With coverage
poetry run pytest -m "unit" --cov=src --cov-report=html --cov-report=term-missing tests/

# With verbose output
poetry run pytest -m "unit" -v tests/
```

### Run Specific Test Files

```bash
# Test specific module
poetry run pytest tests/test_lunarcrush_client.py -m "unit"

# Test specific function
poetry run pytest tests/test_lunarcrush_client.py::TestLunarCrushClient::test_get_current_metrics -m "unit"

# Test with keyword filter
poetry run pytest -k "test_token_bucket" -m "unit"
```

### Generate Coverage Report

```bash
# Generate HTML coverage report
poetry run pytest --cov=src --cov-report=html --cov-report=term-missing -m "unit"

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### View Coverage Results

Coverage results will be displayed in the terminal and saved to:
- Terminal output: Summary with missing lines
- `htmlcov/index.html`: Detailed HTML report
- `coverage.xml`: XML format for CI/CD integration

**Expected Output**:
```
---------- coverage: platform linux, python 3.13.0 -----------
Name                              Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
src/exceptions.py                    25      0   100%
src/lunarcrush_client.py           245     15    94%   123-125, 234-236
src/adapters/i_s3_storage.py        15      0   100%
src/adapters/s3_storage.py          89      8    91%   67-70, 123-126
-----------------------------------------------------------------------
TOTAL                              374     23    94%
```

**Time Estimate**: 30-60 seconds for unit test suite

---

## Integration Tests Execution

Integration tests require real API access and optionally S3 storage.

### Prerequisites for Integration Tests

1. **API Key**: Valid LunarCrush API key in `.env.local`
2. **Enable Integration Tests**:
   ```bash
   export ENABLE_INTEGRATION_TESTS=true
   ```
3. **S3 Access**: Either LocalStack running or AWS credentials configured

### Commands to Run Integration Tests

#### Using the Integration Test Runner (Recommended):

```bash
# Run all integration tests with setup
poetry run python tests/integration/run_integration_tests.py

# Run with specific pytest options
poetry run python tests/integration/run_integration_tests.py -- -k "test_api" --maxfail=1

# Run with coverage
poetry run python tests/integration/run_integration_tests.py -- --cov=src --cov-report=html

# Check prerequisites only
poetry run python tests/integration/run_integration_tests.py --check-only

# Setup environment only
poetry run python tests/integration/run_integration_tests.py --setup-only
```

#### Using pytest directly:

```bash
# Run all integration tests
poetry run pytest -m "integration" tests/integration/

# Run specific integration test
poetry run pytest tests/integration/test_api_integration.py -m "integration"

# Run with verbose output
poetry run pytest -m "integration" -v tests/integration/
```

### Run Integration Tests with LocalStack

1. **Start LocalStack**:
   ```bash
   docker-compose up -d localstack
   ```

2. **Run tests**:
   ```bash
   export ENABLE_INTEGRATION_TESTS=true
   export LOCALSTACK_ENDPOINT=http://localhost:4566
   poetry run pytest -m "integration and localstack" tests/integration/
   ```

### Run Integration Tests with Real AWS S3

1. **Configure AWS credentials**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

2. **Run tests**:
   ```bash
   export ENABLE_INTEGRATION_TESTS=true
   unset LOCALSTACK_ENDPOINT  # Ensure LocalStack is not used
   poetry run pytest -m "integration and aws" tests/integration/
   ```

### Note About Accessing Actual APIs

- **Real API Access**: Integration tests make actual calls to LunarCrush API
- **Rate Limits**: Be aware of LunarCrush rate limits (500 requests/day, 21 requests/hour)
- **Costs**: Free tier is limited, monitor your usage
- **Data Validation**: Tests validate real API responses and data structures

**Time Estimate**: 2-5 minutes for integration test suite (depends on API response times)

---

## E2E Tests Execution

E2E tests require Docker environment and test the complete application workflow.

### Docker Environment Setup

1. **Ensure Docker is running**:
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Enable E2E Tests**:
   ```bash
   export ENABLE_E2E_TESTS=true
   ```

### Commands to Start Docker Containers

```bash
# Start all services (Lambda + LocalStack)
docker-compose up -d

# Start specific service
docker-compose up -d localstack
docker-compose up -d lambda

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Commands to Run E2E Tests

```bash
# Run all E2E tests
poetry run pytest -m "e2e" tests/e2e/

# Run with verbose output
poetry run pytest -m "e2e" -v tests/e2e/

# Run specific E2E test
poetry run pytest tests/e2e/test_complete_workflow.py -m "e2e"

# Run with performance monitoring
poetry run pytest -m "e2e and performance" tests/e2e/
```

### Run Specific E2E Test Categories

```bash
# Run workflow tests
poetry run pytest -m "e2e and workflow" tests/e2e/

# Run performance tests
poetry run pytest -m "e2e and performance" tests/e2e/

# Run error scenario tests
poetry run pytest -m "e2e and error" tests/e2e/

# Run Docker-specific tests
poetry run pytest -m "e2e and docker" tests/e2e/
```

### Cleanup Procedures

```bash
# Stop and remove containers
docker-compose down -v

# Remove all Docker images (optional)
docker system prune -a

# Clean up test data
rm -rf tests/integration/data/*
rm -rf htmlcov/
rm -rf .coverage
```

**Time Estimate**: 5-10 minutes for E2E test suite (includes Docker startup)

---

## Docker Application Execution

### Build Docker Containers

```bash
# Build Lambda container
docker build -t lunarcrush-lambda .

# Build using docker-compose
docker-compose build

# Build without cache
docker-compose build --no-cache
```

### Start Application with Docker Compose

```bash
# Start all services
docker-compose up -d

# Start with environment file
docker-compose --env-file .env.local up -d

# Start and follow logs
docker-compose up -f

# Start specific services
docker-compose up -d localstack
docker-compose up -d lambda
```

### Test Lambda Function Locally

```bash
# Wait for services to be ready (30-60 seconds)
sleep 60

# Test Lambda function with curl
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC", "ETH", "ADA"],
    "parameters": {
      "include_historical": true
    }
  }'

# Test with larger symbol set
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC", "ETH", "ADA", "DOT", "LINK", "BNB", "XRP", "SOL", "AVAX", "MATIC"]
  }'
```

### Access LocalStack S3

```bash
# List S3 buckets
aws s3 ls --endpoint-url=http://localhost:4566

# List bucket contents
aws s3 ls s3://local-test-bucket --endpoint-url=http://localhost:4566

# Download stored metrics
aws s3 cp s3://local-test-bucket/candidates.json ./downloaded_metrics.json --endpoint-url=http://localhost:4566

# Access LocalStack UI (if available)
open http://localhost:4566  # LocalStack dashboard
```

### Example curl Commands to Test Application

```bash
# Basic test
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC"]}'

# Test with parameters
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC", "ETH"],
    "parameters": {
      "include_historical": true,
      "cache_ttl": 300
    }
  }'

# Test error handling (invalid symbol)
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["INVALID_SYMBOL"]}'

# Test rate limiting (multiple rapid requests)
for i in {1..5}; do
  curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
    -H "Content-Type: application/json" \
    -d '{"symbols": ["BTC"]}' &
done
wait
```

**Expected Response Format**:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": "{\"success\": true, \"data\": {\"metrics\": [...], \"metadata\": {...}}}"
}
```

**Time Estimate**: 2-3 minutes for Docker startup, 5-30 seconds per Lambda invocation

---

## Troubleshooting Section

### Common Issues and Solutions

#### 1. Environment Variable Problems

**Issue**: Tests failing with "Missing required environment variables"

**Solution**:
```bash
# Check if .env.local exists
ls -la .env.local

# Verify variables are loaded
env | grep LUNARCRUSH
env | grep S3_BUCKET

# Manually export variables
export LUNARCRUSH_API_KEY=your_key_here
export S3_BUCKET_NAME=your_bucket_here
```

#### 2. Docker Connectivity Issues

**Issue**: Docker containers not starting or not accessible

**Solution**:
```bash
# Check Docker status
docker --version
docker-compose --version
docker ps

# Check if ports are available
netstat -tulpn | grep :9000
netstat -tulpn | grep :4566

# Restart Docker daemon
sudo systemctl restart docker  # Linux
# Restart Docker Desktop  # macOS/Windows

# Clean up Docker resources
docker-compose down -v
docker system prune -a
```

#### 3. API Rate Limiting Issues

**Issue**: LunarCrush API returning 429 errors

**Solution**:
```bash
# Check current rate limits
grep -i "rate" .env.local

# Increase delay between requests
export API_REQUEST_DELAY_SECONDS=5

# Reduce concurrent requests
pytest -m "integration" -n 1  # Single thread

# Monitor API usage
curl -H "Authorization: Bearer $LUNARCRUSH_API_KEY" \
  https://api.lunarcrush.com/v2/usage
```

#### 4. S3/LocalStack Connection Issues

**Issue**: Unable to connect to S3 storage

**Solution**:
```bash
# Check LocalStack health
curl http://localhost:4566/health

# Verify S3 bucket exists
aws s3 ls --endpoint-url=http://localhost:4566

# Create bucket if needed
aws s3 mb s3://local-test-bucket --endpoint-url=http://localhost:4566

# Check AWS credentials (for real S3)
aws sts get-caller-identity
```

#### 5. Python Dependency Issues

**Issue**: Import errors or missing packages

**Solution**:
```bash
# Reinstall dependencies
poetry install --with test,integration,e2e

# Check Python version
python --version  # Should be 3.13+

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Create fresh virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
pip install poetry
poetry install --with test,integration,e2e
```

#### 6. Test Discovery Issues

**Issue**: Pytest not finding tests

**Solution**:
```bash
# Check test structure
find tests/ -name "test_*.py"

# Run with explicit path
poetry run pytest tests/test_lunarcrush_client.py

# Check pytest configuration
cat pyproject.toml | grep -A 20 "\[tool.pytest"

# Run with markers
poetry run pytest -m "unit" tests/
```

### Performance Issues

#### Slow Test Execution

**Solution**:
```bash
# Run tests in parallel
poetry run pytest -n auto -m "unit"

# Use faster coverage
poetry run pytest --cov=src --cov-report=term -m "unit"

# Skip slow tests
poetry run pytest -m "unit and not slow" tests/

# Profile test execution
poetry run pytest --profile -m "unit" tests/
```

#### Memory Issues

**Solution**:
```bash
# Limit test parallelization
poetry run pytest -n 2 -m "unit"

# Run tests sequentially
poetry run pytest -m "unit" -p no:xdist

# Monitor memory usage
poetry run pytest -m "unit" --tb=short | grep -E "(MEMORY|RSS)"
```

---

## Quick Reference Commands

### All-in-One Commands

```bash
# Complete test suite (unit + integration + e2e)
#!/bin/bash
set -e

echo "🧪 Running Unit Tests..."
poetry run pytest -m "unit" --cov=src --cov-report=html tests/

echo "🔗 Running Integration Tests..."
export ENABLE_INTEGRATION_TESTS=true
poetry run python tests/integration/run_integration_tests.py

echo "🐳 Running E2E Tests..."
export ENABLE_E2E_TESTS=true
docker-compose up -d
sleep 60
poetry run pytest -m "e2e" tests/e2e/
docker-compose down -v

echo "✅ All tests completed!"
```

### Copy-Paste Ready Commands

#### Unit Tests
```bash
# Run all unit tests with coverage
poetry run pytest -m "unit" --cov=src --cov-report=html --cov-report=term-missing tests/

# Run specific test file
poetry run pytest tests/test_lunarcrush_client.py -m "unit" -v
```

#### Integration Tests
```bash
# Setup and run integration tests
export ENABLE_INTEGRATION_TESTS=true
poetry run python tests/integration/run_integration_tests.py

# Run with LocalStack
docker-compose up -d localstack
export LOCALSTACK_ENDPOINT=http://localhost:4566
poetry run pytest -m "integration and localstack" tests/integration/
```

#### E2E Tests
```bash
# Complete E2E test run
export ENABLE_E2E_TESTS=true
docker-compose up -d
sleep 60
poetry run pytest -m "e2e" tests/e2e/
docker-compose down -v
```

#### Docker Application
```bash
# Start application
docker-compose up -d

# Test Lambda function
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC", "ETH"]}'

# Check logs
docker-compose logs -f lambda

# Stop application
docker-compose down -v
```

### Resource Requirements

| Test Type | CPU | Memory | Disk | Network | Time |
|-----------|-----|--------|------|---------|------|
| Unit Tests | 1-2 cores | 512MB | 100MB | No | 30-60s |
| Integration Tests | 1-2 cores | 1GB | 200MB | Yes | 2-5m |
| E2E Tests | 2-4 cores | 2GB | 500MB | Yes | 5-10m |
| Docker App | 2-4 cores | 2GB | 1GB | Yes | 2-3m startup |

### Safety Notes

1. **API Usage**: Monitor LunarCrush API usage to avoid exceeding rate limits
2. **AWS Costs**: Be aware of potential AWS costs when using real S3
3. **Docker Resources**: Monitor Docker resource usage during E2E tests
4. **Data Privacy**: Test data may contain real cryptocurrency metrics
5. **Network Security**: Ensure secure handling of API keys and credentials

### Environment Checklist

- [ ] Python 3.13+ installed
- [ ] Docker and Docker Compose installed
- [ ] `.env.local` file configured with API keys
- [ ] Dependencies installed: `poetry install --with test,integration,e2e`
- [ ] Ports 9000 and 4566 available
- [ ] Sufficient disk space (1GB+)
- [ ] Network connectivity for API access

---

## Additional Resources

- [LunarCrush API Documentation](https://lunarcrush.com/developers/api)
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

For issues specific to this project, check the project's GitHub issues or create a new one with detailed error messages and environment information.