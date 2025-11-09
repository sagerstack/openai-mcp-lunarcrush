# Implementation Plan: US-001 Extract Social Metrics

## Metadata

| Field | Value |
|-------|-------|
| ID | US-001-IMPL-PLAN |
| Title | Extract Social Metrics Implementation Plan |
| User Story ID | US-001 |
| Tech Research ID | US-001-tech-research.md |
| Created | 2025-11-09 19:41:00 |
| Status | Draft |
| Status History | [2025-11-09 19:41:00: Draft - Initial implementation plan creation] |
| Last Updated | 2025-11-09 19:41:00 |
| GitHub Issue | [Issue link when created] |
| Complexity | High (Multiple API endpoints, rate limiting, data processing) |
| Dependencies | LunarCrush API access (v1 endpoints only), AWS Lambda, S3 storage |

## Quick Reference

### Tech Stack
- **Runtime**: Python 3.13
- **HTTP Client**: requests 2.31.0+
- **AWS SDK**: boto3 1.34.0+
- **Logging**: structlog 23.1.0+
- **Testing**: pytest 7.4.0+
- **Containerization**: Docker 24.0+

### Architectural Pattern
Serverless Lambda function with S3 storage, implementing token bucket rate limiting and percentage change calculations.

### Technical Research Reference
[US-001-tech-research.md](../../US-001-tech-research.md) - Complete API specifications, field mappings, and implementation considerations.

## Requirements Coverage Validation

### Functional Requirements
| Requirement ID | Description | Parent Task | Status |
|----------------|-------------|-------------|--------|
| FR-1 | Extract Current Social Metrics | [5.0][FR-1] (5 subtasks) | [ ] |
| FR-2 | Extract Historical Social Metrics | [6.0][FR-2] (5 subtasks) | [ ] |
| FR-3 | Calculate 24-Hour Percentage Changes | [7.0][FR-3] (5 subtasks) | [ ] |
| FR-4 | Batch Processing | [8.0][FR-4] (4 subtasks) | [ ] |
| FR-5 | Validate API Responses | [9.0][FR-5] (4 subtasks) | [ ] |

### Technical Requirements
| Requirement ID | Description | Parent Task | Status |
|----------------|-------------|-------------|--------|
| TR-1 | API Rate Limit Management | [10.0][TR-1] (5 subtasks) | [ ] |
| TR-2 | Response Time <30s for 50 assets | [11.0][TR-2] (4 subtasks) | [ ] |
| TR-3 | Error Handling with 99% success rate | [12.0][TR-3] (5 subtasks) | [ ] |
| TR-4 | Percentage Change Calculation Accuracy | [13.0][TR-4] (4 subtasks) | [ ] |
| TR-5 | Metric Caching (5-minute) | [14.0][TR-5] (4 subtasks) | [ ] |
| TR-6 | API Key Security | [15.0][TR-6] (4 subtasks) | [ ] |
| TR-7 | AWS Lambda Deployment | [16.0][TR-7] (5 subtasks) | [ ] |
| TR-8 | S3 Storage for JSON Files | [17.0][TR-8] (5 subtasks) | [ ] |
| TR-9 | Environment Variables Configuration | [18.0][TR-9] (4 subtasks) | [ ] |
| TR-10 | IAM Roles and Permissions | [19.0][TR-10] (4 subtasks) | [ ] |

### Acceptance Criteria
| Criteria ID | Description | Parent Task | Unit Tests | Integration Tests | E2E Test | Live Verification |
|-------------|-------------|-------------|------------|-------------------|----------|-------------------|
| AC-1 | Extract current social metrics for specified symbols | [20.0][AC-1] (7 subtasks) | [20.4] | [20.5] | [20.6] | [20.7] |
| AC-2 | Retrieve historical time series data for past 24 hours | [21.0][AC-2] (7 subtasks) | [21.4] | [21.5] | [21.6] | [21.7] |
| AC-3 | Calculate accurate 24-hour percentage changes | [22.0][AC-3] (7 subtasks) | [22.4] | [22.5] | [22.6] | [22.7] |
| AC-4 | Process multiple symbols efficiently within API rate limits | [23.0][AC-4] (7 subtasks) | [23.4] | [23.5] | [23.6] | [23.7] |
| AC-5 | Handle missing data gracefully and log validation errors | [24.0][AC-5] (7 subtasks) | [24.4] | [24.5] | [24.6] | [24.7] |
| AC-6 | Implement throttling to stay within 500 requests/day limit | [25.0][AC-6] (7 subtasks) | [25.4] | [25.5] | [25.6] | [25.7] |
| AC-7 | Implement retry logic with exponential backoff | [26.0][AC-7] (7 subtasks) | [26.4] | [26.5] | [26.6] | [26.7] |
| AC-8 | Return cached values if within 5-minute cache window | [27.0][AC-8] (7 subtasks) | [27.4] | [27.5] | [27.6] | [27.7] |
| AC-9 | Return complete dataset with current values and 24-hour changes | [28.0][AC-9] (7 subtasks) | [28.4] | [28.5] | [28.6] | [28.7] |
| AC-10 | Lambda function executes successfully within timeout and memory limits | [29.0][AC-10] (7 subtasks) | [29.4] | [29.5] | [29.6] | [29.7] |
| AC-11 | Create properly formatted JSON files in S3 bucket with correct naming | [30.0][AC-11] (7 subtasks) | [30.4] | [30.5] | [30.6] | [30.7] |
| AC-12 | Docker environment starts successfully and application accessible locally | [31.0][AC-12] (7 subtasks) | [31.4] | [31.5] | [31.6] | [31.7] |
| AC-13 | System loads all required configuration from environment variables | [32.0][AC-13] (7 subtasks) | [32.4] | [32.5] | [32.6] | [32.7] |
| AC-14 | Log detailed error information to CloudWatch and handle gracefully | [33.0][AC-14] (7 subtasks) | [33.4] | [33.5] | [33.6] | [33.7] |

**Coverage Summary**:
- ✅ Functional Requirements: 5/5 mapped (100%)
- ✅ Technical Requirements: 10/10 mapped (100%)
- ✅ Acceptance Criteria: 14/14 mapped with complete test coverage (100%)

## Task-Based Implementation Plan

### Execution Instructions
Complete tasks in order: Manual Prerequisites → Environment & Setup → Functional Requirements → Technical Requirements → Acceptance Criteria → Documentation & Deployment

---

### 1. Manual Prerequisites

- [x] **[1.0][MANUAL] External Service Provisioning**
  - [x] [1.1][MANUAL] Subscribe to LunarCrush Individual Plan ($30/month) at https://lunarcrush.com/pricing
  - [x] [1.2][MANUAL] Navigate to Dashboard > Developers > API > Authentication
  - [x] [1.3][MANUAL] Generate API key and copy to .env.local
  - [x] [1.4][MANUAL] Test API key with curl command:
    ```bash
    curl -H "Authorization: Bearer <API_KEY>" "https://lunarcrush.com/api4/public/coins/list/v1?limit=1"
    ```

- [ ] **[2.0][MANUAL] AWS Infrastructure Setup**
  - [ ] [2.1][MANUAL] Create S3 bucket for metrics storage with appropriate naming convention
  - [ ] [2.2][MANUAL] Create AWS Systems Manager Parameter Store entry for encrypted API key
  - [ ] [2.3][MANUAL] Create IAM role for Lambda function with S3 and Parameter Store access
  - [ ] [2.4][MANUAL] Note bucket name, parameter path, and role ARN for configuration

---

### 2. Environment & Setup

- [x] **[3.0][SETUP] Development Environment Setup**
  - [x] [3.1] Verify Python 3.13 installed
  - [x] [3.2] Create virtual environment using poetry (Python 3.13.3 confirmed)
  - [x] [3.3] Install dependencies: requests, boto3, structlog, pytest
  - [x] [3.4] Update pyproject.toml with exact versions from tech research
  - [x] [3.5] Create .env.example template with all required variables

- [ ] **[4.0][SETUP] Docker Infrastructure**
  - [ ] [4.1] Create Dockerfile with Python 3.13 base as specified in tech research
  - [ ] [4.2] Create docker-compose.yml with Lambda and LocalStack services
  - [ ] [4.3] Configure volume mounts for .env.local and source code
  - [ ] [4.4] Test Docker build: `docker-compose build`

- [ ] **[5.0][SETUP] Exception Hierarchy**
  - [ ] [5.1] Implement LunarCrushAPIError (base exception)
  - [ ] [5.2] Implement LunarCrushRateLimitError (429)
  - [ ] [5.3] Implement LunarCrushAuthenticationError (401)
  - [ ] [5.4] Implement LunarCrushNetworkError (connection issues)
  - [ ] [5.5] Implement LunarCrushDataValidationError (invalid response format)

---

### 3. Functional Requirements

- [ ] **[6.0][FR-1] Extract Current Social Metrics**
  - [ ] [6.1] Query LunarCrush /coins/list/v1 endpoint: GET https://lunarcrush.com/api4/public/coins/list/v1
    - Request parameters: sort, filter, limit, desc, page
    - Authentication: Bearer token from Parameter Store
  - [ ] [6.2] Parse response and extract fields per tech research mapping:
    - Extract `data[].interactions_24h` → store as `interactions_24h` (Integer)
    - Extract `data[].social_volume_24h` → store as `social_volume_24h` (Integer)
    - Extract `data[].social_dominance` → store as `social_dominance` (Float)
    - Extract `data[].galaxy_score` → store as `galaxy_score` (Float)
    - Extract `data[].galaxy_score_previous` → store as `galaxy_score_previous` (Float)
    - Extract `data[].sentiment` → store as `sentiment` (Integer)
    - Extract `data[].alt_rank` → store as `alt_rank` (Integer)
    - Extract `data[].alt_rank_previous` → store as `alt_rank_previous` (Integer)
  - [ ] [6.3] Validate extracted data matches expected structure:
    - Assert `interactions_24h` is not None and >= 0
    - Assert `social_volume_24h` is not None and >= 0
    - Assert `social_dominance` is not None and >= 0
    - Assert `galaxy_score` is not None and >= 0
    - Assert `sentiment` is not None and >= 0
    - Assert `alt_rank` is not None and >= 1
    - Log extraction: logger.debug("Extracted current metrics", symbol=symbol, interactions=interactions_24h)
  - [ ] [6.4] Handle missing/malformed fields:
    - If `symbol` missing → log error, skip record
    - If `interactions_24h` missing → use default value 0
    - If `social_dominance` missing → use default value 0.0
  - [ ] [6.5] Integration test: Verify extraction with real API call
    - Call real API (use .env.local credentials)
    - Assert extracted fields match tech research documentation
    - Assert field types match domain model

- [ ] **[7.0][FR-2] Extract Historical Social Metrics**
  - [ ] [7.1] Query LunarCrush /coins/{symbol}/time-series/v1 endpoint: GET https://lunarcrush.com/api4/public/coins/{symbol}/time-series/v1
    - Request parameters: coin (symbol), bucket=hour, interval=1h, start=-24h, end=now
    - Authentication: Bearer token from Parameter Store
  - [ ] [7.2] Parse response and extract fields per tech research mapping:
    - Extract `data[].interactions` → store as `historical_interactions` (Integer)
    - Extract `data[].posts_active` → store as `historical_posts_active` (Integer)
    - Extract `data[].sentiment` → store as `historical_sentiment` (Integer)
    - Extract `data[].social_dominance` → store as `historical_social_dominance` (Float)
  - [ ] [7.3] Validate extracted data matches expected structure:
    - Assert `historical_interactions` is not None and >= 0
    - Assert `historical_posts_active` is not None and >= 0
    - Assert `historical_sentiment` is not None and >= 0
    - Assert `historical_social_dominance` is not None and >= 0
    - Log extraction: logger.debug("Extracted historical metrics", symbol=symbol, time_range="24h")
  - [ ] [7.4] Handle missing/malformed fields:
    - If `data` array empty → log warning, use default values
    - If time series incomplete → interpolate missing points
  - [ ] [7.5] Integration test: Verify extraction with real API call
    - Call real API for test symbol (BTC)
    - Assert extracted fields match expected time series format
    - Assert 24-hour data range is complete

- [ ] **[8.0][FR-3] Calculate 24-Hour Percentage Changes**
  - [ ] [8.1] Implement percentage change calculation functions per tech research formulas:
    - interactions_24h_pct: ((current - previous_24h) / previous_24h) * 100
    - social_volume_24h_pct: ((current_posts_active - previous_24h_posts_active) / previous_24h_posts_active) * 100
    - social_dominance_pct: ((current_dominance - previous_24h_dominance) / previous_24h_dominance) * 100
    - galaxy_score_change: galaxy_score - galaxy_score_previous
    - sentiment_pct: ((current_sentiment - previous_24h_sentiment) / previous_24h_sentiment) * 100
    - alt_rank_change: alt_rank_previous - alt_rank
  - [ ] [8.2] Implement edge case handling per tech research:
    - If previous_24h = 0 → change = current
    - If previous_posts_active = 0 → change = current_posts_active
    - If previous_dominance = 0 → change = current_dominance
    - If previous_sentiment = 0 → change = current_sentiment
  - [ ] [8.3] Validate calculation results:
    - Assert percentage changes are numeric
    - Assert galaxy_score_change and alt_rank_change are integers
    - Log calculations: logger.debug("Calculated changes", symbol=symbol, interactions_pct=interactions_24h_pct)
  - [ ] [8.4] Write unit tests: Test all calculation formulas with edge cases
  - [ ] [8.5] Live test: Verify calculations with real API data

- [ ] **[9.0][FR-4] Batch Processing**
  - [ ] [9.1] Implement batch processing for multiple cryptocurrency symbols
  - [ ] [9.2] Add parallel processing with asyncio for concurrent API calls
  - [ ] [9.3] Implement batch size configuration to respect API limits
  - [ ] [9.4] Write unit tests: Test batch processing with various symbol counts

- [ ] **[10.0][FR-5] Validate API Responses**
  - [ ] [10.1] Implement response schema validation for both endpoints
  - [ ] [10.2] Add data range validation for all extracted metrics
  - [ ] [10.3] Implement missing data detection and reporting
  - [ ] [10.4] Write unit tests: Test validation with valid and invalid responses

---

### 4. Technical Requirements

- [ ] **[11.0][TR-1] API Rate Limit Management**
  - [ ] [11.1] Implement token bucket algorithm for rate limiting
  - [ ] [11.2] Configure daily limit: 500 requests/day
  - [ ] [11.3] Add CloudWatch metrics for API usage tracking
  - [ ] [11.4] Implement request queuing with exponential backoff
  - [ ] [11.5] Write unit tests: Test rate limiting behavior

- [ ] **[12.0][TR-2] Response Time <30s for 50 assets**
  - [ ] [12.1] Implement performance measurement instrumentation
  - [12.2] Optimize API calls with connection pooling
  - [ ] [12.3] Add parallel processing for multiple symbols
  - [ ] [12.4] Performance test: Process 50 assets within 30 seconds

- [ ] **[13.0][TR-3] Error Handling with 99% success rate**
  - [ ] [13.1] Implement structured exception handling for all API calls
  - [ ] [13.2] Add retry logic with exponential backoff and jitter
  - [ ] [13.3] Implement circuit breaker pattern for API failures
  - [ ] [13.4] Add comprehensive error logging with context
  - [ ] [13.5] Write unit tests: Test error scenarios and recovery

- [ ] **[14.0][TR-4] Percentage Change Calculation Accuracy**
  - [ ] [14.1] Implement precise decimal arithmetic for calculations
  - [ ] [14.2] Add validation for calculation results
  - [ ] [14.3] Implement rounding to appropriate decimal places
  - [ ] [14.4] Write unit tests: Test calculation accuracy with known inputs

- [ ] **[15.0][TR-5] Metric Caching (5-minute)**
  - [ ] [15.1] Implement in-memory caching with 5-minute TTL
  - [ ] [15.2] Add cache key generation based on symbol and timestamp
  - [ ] [15.3] Implement cache invalidation strategy
  - [ ] [15.4] Write unit tests: Test cache behavior and expiration

- [ ] **[16.0][TR-6] API Key Security**
  - [ ] [16.1] Implement Parameter Store integration for encrypted API key
  - [ ] [16.2] Add API key validation and format checking
  - [ ] [16.3] Ensure API key never logged or exposed in responses
  - [ ] [16.4] Write unit tests: Test secure key handling

- [ ] **[17.0][TR-7] AWS Lambda Deployment**
  - [ ] [17.1] Create Lambda function handler with Python 3.13 runtime
  - [ ] [17.2] Configure Lambda settings: 512MB memory, 5-minute timeout
  - [ ] [17.3] Implement Lambda environment variable configuration
  - [ ] [17.4] Add CloudWatch logging integration
  - [ ] [17.5] Write unit tests: Test Lambda handler with mock events

- [ ] **[18.0][TR-8] S3 Storage for JSON Files**
  - [ ] [18.1] Implement S3 client with proper configuration
  - [ ] [18.2] Create JSON formatter for metrics output structure
  - [ ] [18.3] Implement file naming convention: candidates.json
  - [ ] [18.4] Add archive management with timestamped files
  - [ ] [18.5] Write unit tests: Test S3 upload and file formatting

- [ ] **[19.0][TR-9] Environment Variables Configuration**
  - [ ] [19.1] Implement environment variable loading with validation
  - [ ] [19.2] Add default values for optional configuration
  - [ ] [19.3] Implement configuration validation on startup
  - [ ] [19.4] Write unit tests: Test configuration loading and validation

- [ ] **[20.0][TR-10] IAM Roles and Permissions**
  - [ ] [20.1] Define least-privilege IAM policy for Lambda function
  - [ ] [20.2] Configure S3 permissions: GetObject, PutObject, DeleteObject, ListBucket
  - [ ] [20.3] Configure Parameter Store permissions: GetParameter, GetParametersByPath
  - [ ] [20.4] Write unit tests: Test IAM permissions with mock AWS calls

---

### 5. Acceptance Criteria

- [ ] **[21.0][AC-1] Extract current social metrics for specified symbols**
  - [ ] [21.1] Implement API client for /coins/list/v1 endpoint
  - [ ] [21.2] Add symbol filtering and data extraction logic
  - [ ] [21.3] Implement response validation and error handling
  - [ ] [21.4] Write unit tests: Mock API responses, verify field extraction
  - [ ] [21.5] Write integration tests: Test API client with test endpoints
  - [ ] [21.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # Test with curl
    response=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["BTC", "ETH"]}')
    
    # Assertions
    echo "$response" | grep -q "interactions_24h" || exit 1
    echo "$response" | grep -q "social_volume_24h" || exit 1
    echo "$response" | grep -q "social_dominance" || exit 1
    echo "$response" | grep -q "galaxy_score" || exit 1
    echo "$response" | grep -q "sentiment" || exit 1
    echo "$response" | grep -q "alt_rank" || exit 1
    
    echo "✅ AC-1 E2E test passed"
    ```
  - [ ] [21.7] **Live Environment Verification**:
    - Deploy Lambda to test environment
    - Invoke with real cryptocurrency symbols
    - Verify all 6 metrics extracted correctly
    - Document API response structure

- [ ] **[22.0][AC-2] Retrieve historical time series data for past 24 hours**
  - [ ] [22.1] Implement API client for /coins/{symbol}/time-series/v1 endpoint
  - [ ] [22.2] Add 24-hour time range parameter configuration
  - [ ] [22.3] Implement historical data parsing and validation
  - [ ] [22.4] Write unit tests: Mock historical API responses
  - [ ] [22.5] Write integration tests: Test historical data extraction
  - [ ] [22.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # Test with curl
    response=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["BTC"], "include_historical": true}')
    
    # Assertions
    echo "$response" | grep -q "historical_interactions" || exit 1
    echo "$response" | grep -q "historical_posts_active" || exit 1
    echo "$response" | grep -q "historical_sentiment" || exit 1
    echo "$response" | grep -q "historical_social_dominance" || exit 1
    
    echo "✅ AC-2 E2E test passed"
    ```
  - [ ] [22.7] **Live Environment Verification**:
    - Deploy to test environment
    - Request historical data for BTC
    - Verify 24-hour time series completeness
    - Document historical data structure

- [ ] **[23.0][AC-3] Calculate accurate 24-hour percentage changes**
  - [ ] [23.1] Implement percentage change calculation module
  - [ ] [23.2] Add edge case handling for zero previous values
  - [ ] [23.3] Integrate calculations with data processing pipeline
  - [ ] [23.4] Write unit tests: Test all calculation formulas with edge cases
  - [ ] [23.5] Write integration tests: Test calculations with real data
  - [ ] [23.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # Test with curl
    response=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["BTC"], "include_changes": true}')
    
    # Assertions
    echo "$response" | grep -q "interactions_24h_pct" || exit 1
    echo "$response" | grep -q "social_volume_24h_pct" || exit 1
    echo "$response" | grep -q "social_dominance_pct" || exit 1
    echo "$response" | grep -q "galaxy_score_change" || exit 1
    echo "$response" | grep -q "sentiment_pct" || exit 1
    echo "$response" | grep -q "alt_rank_change" || exit 1
    
    echo "✅ AC-3 E2E test passed"
    ```
  - [ ] [23.7] **Live Environment Verification**:
    - Deploy to test environment
    - Process symbols with known previous values
    - Verify calculation accuracy with manual calculations
    - Document calculation formulas and examples

- [ ] **[24.0][AC-4] Process multiple symbols efficiently within API rate limits**
  - [ ] [24.1] Implement batch processing with configurable batch sizes
  - [ ] [24.2] Add rate limiting with token bucket algorithm
  - [ ] [24.3] Implement parallel processing for multiple symbols
  - [ ] [24.4] Write unit tests: Test batch processing with various sizes
  - [ ] [24.5] Write integration tests: Test rate limiting behavior
  - [ ] [24.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # Test with curl - 50 symbols
    symbols=$(printf '"BTC%02d",' {1..50} | sed 's/,$//')
    response=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d "{\"symbols\": [$symbols]}")
    
    # Assertions
    echo "$response" | jq '.metrics | length' | grep -q "50" || exit 1
    echo "$response" | jq '.metrics[0] | has("symbol")' | grep -q "true" || exit 1
    
    echo "✅ AC-4 E2E test passed"
    ```
  - [ ] [24.7] **Live Environment Verification**:
    - Deploy to test environment
    - Process 50 symbols in single request
    - Verify completion within 30 seconds
    - Monitor API usage to stay within limits

- [ ] **[25.0][AC-5] Handle missing data gracefully and log validation errors**
  - [ ] [25.1] Implement data validation with comprehensive error checking
  - [ ] [25.2] Add graceful handling for missing or invalid fields
  - [ ] [25.3] Implement structured logging for validation errors
  - [ ] [25.4] Write unit tests: Test validation with various data issues
  - [ ] [25.5] Write integration tests: Test error handling scenarios
  - [ ] [25.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # Test with invalid symbol
    response=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["INVALIDSYMBOL"]}')
    
    # Assertions - should handle gracefully
    echo "$response" | grep -q "error" || exit 1
    echo "$response" | grep -q "validation" || exit 1
    
    echo "✅ AC-5 E2E test passed"
    ```
  - [ ] [25.7] **Live Environment Verification**:
    - Deploy to test environment
    - Test with invalid symbols and malformed data
    - Verify graceful error handling and logging
    - Check CloudWatch logs for validation errors

- [ ] **[26.0][AC-6] Implement throttling to stay within 500 requests/day limit**
  - [ ] [26.1] Implement token bucket rate limiting with daily quota
  - [ ] [26.2] Add request counting and quota tracking
  - [ ] [26.3] Implement throttling when approaching daily limit
  - [ ] [26.4] Write unit tests: Test rate limiting with various scenarios
  - [ ] [26.5] Write integration tests: Test throttling behavior
  - [ ] [26.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # Test with many requests to trigger throttling
    for i in {1..10}; do
      response=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
        -d '{"symbols": ["BTC"]}')
      echo "Request $i: $(echo "$response" | jq -r '.status // "error"')"
    done
    
    echo "✅ AC-6 E2E test passed"
    ```
  - [ ] [26.7] **Live Environment Verification**:
    - Deploy to test environment
    - Monitor API usage with CloudWatch metrics
    - Verify throttling activates when approaching limit
    - Document rate limiting behavior

- [ ] **[27.0][AC-7] Implement retry logic with exponential backoff**
  - [ ] [27.1] Implement retry mechanism with exponential backoff
  - [ ] [27.2] Add jitter to prevent thundering herd
  - [ ] [27.3] Configure retry limits and timeout handling
  - [ ] [27.4] Write unit tests: Test retry behavior with various failures
  - [ ] [27.5] Write integration tests: Test retry with simulated failures
  - [ ] [27.6] **E2E Test**:
    ```bash
    # Build and deploy with mock failure scenario
    docker-compose build
    docker-compose up -d
    
    # Test retry behavior
    response=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["BTC"], "simulate_failure": true}')
    
    # Assertions - should retry and eventually succeed or fail gracefully
    echo "$response" | grep -q "retry" || exit 1
    
    echo "✅ AC-7 E2E test passed"
    ```
  - [ ] [27.7] **Live Environment Verification**:
    - Deploy to test environment
    - Test retry behavior with network failures
    - Verify exponential backoff timing
    - Document retry configuration

- [ ] **[28.0][AC-8] Return cached values if within 5-minute cache window**
  - [ ] [28.1] Implement in-memory caching with 5-minute TTL
  - [ ] [28.2] Add cache key generation based on symbol and timestamp
  - [ ] [28.3] Implement cache hit/miss tracking
  - [ ] [28.4] Write unit tests: Test cache behavior and expiration
  - [ ] [28.5] Write integration tests: Test cache with API calls
  - [ ] [28.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # First request - should hit API
    response1=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["BTC"]}')
    
    # Second request within 5 minutes - should hit cache
    response2=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["BTC"]}')
    
    # Assertions - both responses should be identical
    test "$response1" = "$response2" || exit 1
    
    echo "✅ AC-8 E2E test passed"
    ```
  - [ ] [28.7] **Live Environment Verification**:
    - Deploy to test environment
    - Make repeated requests for same symbol
    - Verify cache hit behavior
    - Document cache performance

- [ ] **[29.0][AC-9] Return complete dataset with current values and 24-hour changes**
  - [ ] [29.1] Implement complete data aggregation pipeline
  - [ ] [29.2] Combine current metrics with calculated changes
  - [ ] [29.3] Format output according to tech research specification
  - [ ] [29.4] Write unit tests: Test data aggregation and formatting
  - [ ] [29.5] Write integration tests: Test complete pipeline
  - [ ] [29.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # Test complete dataset
    response=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["BTC"], "include_changes": true}')
    
    # Assertions
    echo "$response" | jq '.metrics[0] | has("current")' | grep -q "true" || exit 1
    echo "$response" | jq '.metrics[0] | has("changes")' | grep -q "true" || exit 1
    echo "$response" | jq '.metrics[0].current | has("interactions_24h")' | grep -q "true" || exit 1
    echo "$response" | jq '.metrics[0].changes | has("interactions_24h_pct")' | grep -q "true" || exit 1
    
    echo "✅ AC-9 E2E test passed"
    ```
  - [ ] [29.7] **Live Environment Verification**:
    - Deploy to test environment
    - Request complete dataset for multiple symbols
    - Verify all current values and changes present
    - Document output structure

- [ ] **[30.0][AC-10] Lambda function executes successfully within timeout and memory limits**
  - [ ] [30.1] Configure Lambda with 512MB memory and 5-minute timeout
  - [ ] [30.2] Implement memory usage monitoring
  - [ ] [30.3] Add execution time tracking
  - [ ] [30.4] Write unit tests: Test memory and time constraints
  - [ ] [30.5] Write integration tests: Test Lambda execution
  - [ ] [30.6] **E2E Test**:
    ```bash
    # Deploy Lambda
    aws lambda create-function --function-name test-social-metrics \
      --runtime python3.13 --handler lambda_function.lambda_handler \
      --role arn:aws:iam::account:role/lambda-exec-role \
      --zip-file fileb://function.zip
    
    # Test execution
    start_time=$(date +%s)
    aws lambda invoke --function-name test-social-metrics \
      --payload '{"symbols": ["BTC"]}' output.json
    end_time=$(date +%s)
    
    # Assertions
    test $((end_time - start_time)) -lt 300 || exit 1  # < 5 minutes
    jq -e '.statusCode == 200' output.json || exit 1
    
    echo "✅ AC-10 E2E test passed"
    ```
  - [ ] [30.7] **Live Environment Verification**:
    - Deploy Lambda to test environment
    - Monitor CloudWatch metrics for memory and duration
    - Verify execution within limits
    - Document performance characteristics

- [ ] **[31.0][AC-11] Create properly formatted JSON files in S3 bucket with correct naming**
  - [ ] [31.1] Implement S3 file upload with proper JSON formatting
  - [ ] [31.2] Add file naming convention: candidates.json
  - [ ] [31.3] Implement archive management with timestamped files
  - [ ] [31.4] Write unit tests: Test S3 upload and file formatting
  - [ ] [31.5] Write integration tests: Test S3 integration
  - [ ] [31.6] **E2E Test**:
    ```bash
    # Build and deploy
    docker-compose build
    docker-compose up -d
    
    # Trigger Lambda function
    curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"symbols": ["BTC"]}'
    
    # Check S3 (using LocalStack)
    aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket/
    aws --endpoint-url=http://localhost:4566 s3 cp s3://test-bucket/candidates.json - \
      | jq '.metrics | length' | grep -q "1" || exit 1
    
    echo "✅ AC-11 E2E test passed"
    ```
  - [ ] [31.7] **Live Environment Verification**:
    - Deploy to test environment
    - Invoke Lambda function
    - Verify S3 file creation and format
    - Check archive file generation

- [ ] **[32.0][AC-12] Docker environment starts successfully and application accessible locally**
  - [ ] [32.1] Create Dockerfile with Python 3.13 base
  - [ ] [32.2] Configure docker-compose.yml with Lambda and LocalStack
  - [ ] [32.3] Add environment variable configuration
  - [ ] [32.4] Write unit tests: Test Docker configuration
  - [ ] [32.5] Write integration tests: Test container communication
  - [ ] [32.6] **E2E Test**:
    ```bash
    # Build and start containers
    docker-compose build
    docker-compose up -d
    
    # Wait for containers to be ready
    sleep 10
    
    # Test Lambda endpoint
    response=$(curl -s http://localhost:9000/2015-03-31/functions/function/invocations \
      -d '{"symbols": ["BTC"]}')
    
    # Assertions
    echo "$response" | grep -q "metrics" || exit 1
    
    # Test LocalStack S3
    aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket/ || exit 1
    
    echo "✅ AC-12 E2E test passed"
    ```
  - [ ] [32.7] **Live Environment Verification**:
    - Run docker-compose in local environment
    - Verify all containers start successfully
    - Test application accessibility
    - Document Docker setup

- [ ] **[33.0][AC-13] System loads all required configuration from environment variables**
  - [ ] [33.1] Implement environment variable loading with validation
  - [ ] [33.2] Add configuration for API key, S3 bucket, and other settings
  - [ ] [33.3] Implement startup validation for required variables
  - [ ] [33.4] Write unit tests: Test configuration loading
  - [ ] [33.5] Write integration tests: Test with various configurations
  - [ ] [33.6] **E2E Test**:
    ```bash
    # Test with missing environment variable
    unset LUNARCRUSH_API_KEY
    docker-compose build
    docker-compose up -d
    
    # Should fail to start
    response=$(curl -s http://localhost:9000/2015-03-31/functions/function/invocations \
      -d '{"symbols": ["BTC"]}')
    echo "$response" | grep -q "error" || exit 1
    
    # Test with all required variables
    export LUNARCRUSH_API_KEY="test-key"
    export S3_BUCKET_NAME="test-bucket"
    docker-compose up -d
    
    # Should work
    response=$(curl -s http://localhost:9000/2015-03-31/functions/function/invocations \
      -d '{"symbols": ["BTC"]}')
    echo "$response" | grep -q "metrics" || exit 1
    
    echo "✅ AC-13 E2E test passed"
    ```
  - [ ] [33.7] **Live Environment Verification**:
    - Deploy Lambda with missing environment variable
    - Verify startup failure
    - Deploy with all required variables
    - Verify successful execution

- [ ] **[34.0][AC-14] Log detailed error information to CloudWatch and handle gracefully**
  - [ ] [34.1] Implement structured logging with CloudWatch integration
  - [ ] [34.2] Add error context and correlation IDs
  - [ ] [34.3] Implement graceful error handling for all failure modes
  - [ ] [34.4] Write unit tests: Test logging with various error scenarios
  - [ ] [34.5] Write integration tests: Test CloudWatch logging
  - [ ] [34.6] **E2E Test**:
    ```bash
    # Deploy Lambda
    aws lambda create-function --function-name test-social-metrics \
      --runtime python3.13 --handler lambda_function.lambda_handler \
      --role arn:aws:iam::account:role/lambda-exec-role \
      --zip-file fileb://function.zip
    
    # Trigger error
    aws lambda invoke --function-name test-social-metrics \
      --payload '{"symbols": ["INVALID"]}' output.json
    
    # Check CloudWatch logs
    log_stream=$(aws logs describe-log-streams --log-group-name /aws/lambda/test-social-metrics \
      --order-by LastEventTime --descending --max-items 1 \
      --query 'logStreams[0].logStreamName' --output text)
    
    aws logs get-log-events --log-group-name /aws/lambda/test-social-metrics \
      --log-stream-name "$log_stream" \
      --query 'events[0].message' --output text | grep -q "error" || exit 1
    
    echo "✅ AC-14 E2E test passed"
    ```
  - [ ] [34.7] **Live Environment Verification**:
    - Deploy to test environment
    - Trigger various error conditions
    - Verify CloudWatch log entries
    - Document error handling behavior

---

### 6. Documentation & Deployment

- [ ] **[35.0][DOC] Developer Documentation**
  - [ ] [35.1] Write setup guide for local development
  - [ ] [35.2] Document API integration and authentication
  - [ ] [35.3] Create troubleshooting guide for common issues
  - [ ] [35.4] Add inline code documentation with examples

- [ ] **[36.0][DOC] Deployment Documentation**
  - [ ] [36.1] Create Lambda deployment guide
  - [ ] [36.2] Document S3 bucket configuration
  - [ ] [36.3] Write IAM role setup instructions
  - [ ] [36.4] Create monitoring and alerting guide

- [ ] **[37.0][DOC] CI/CD Pipeline**
  - [ ] [37.1] Create .github/workflows/ci.yml
  - [ ] [37.2] Add stages: build → unit → integration → E2E → live tests
  - [ ] [37.3] Configure pipeline to run all test levels
  - [ ] [37.4] Add deployment stage for Lambda function

- [ ] **[38.0][DOC] Code Quality & Version Control**
  - [ ] [38.1] Run code formatter: black
  - [ ] [38.2] Run linter: flake8
  - [ ] [38.3] Run type checker: mypy
  - [ ] [38.4] Fix all issues
  - [ ] [38.5] Create commit with descriptive message
  - [ ] [38.6] Push to feature branch
  - [ ] [38.7] Create pull request with DoD checklist

---

## Changelog

| Date | Author | Summary | Sections Affected | Reason |
|------|--------|---------|------------------|--------|
| 2025-11-09 19:41:00 | Solution Architect | Initial implementation plan creation | All sections | Complete task breakdown with requirements coverage |