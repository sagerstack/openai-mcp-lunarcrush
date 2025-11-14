# User Story: Extract Social Metrics

## Metadata
| Field | Value |
|-------|-------|
| ID | US-001 |
| Title | Extract Social Metrics |
| Epic Reference | EP-001 |
| MVP Reference | MVP-001 |
| Created | 2025-11-09 08:36:00 |
| Status | Draft |
| Status History | [2025-11-09 08:36:00: Draft - Initial story creation] |
| Last Updated | 2025-11-09 08:44:00 |
| GitHub Issue | [Issue link when created] |

## Story Overview
- **Story Purpose**: Extract key social metrics from LunarCrush API to enable comprehensive social media analysis for cryptocurrency assets
- **Epic Context**: Part of building a complete social analytics system for cryptocurrency monitoring
- **User Impact**: Enables users to track social sentiment and engagement metrics for informed decision-making
- **Business Value**: Provides critical social intelligence for cryptocurrency trading and investment strategies

## User Story

| Field | Value |
|-------|-------|
| **As a** | cryptocurrency analyst |
| **I want** | to extract key social metrics from LunarCrush API |
| **So that** | I can analyze social sentiment and engagement trends for cryptocurrency assets |
| **User Persona** | Cryptocurrency Analyst |
| **Use Case** | Social Media Analysis for Trading Decisions |
| **User Journey Step** | Data Collection & Analysis |
| **Business Context** | Cryptocurrency trading and investment platform |
| **User Value** | Access to real-time social metrics for informed trading decisions |
| **Business Value** | Enhanced trading platform with social intelligence capabilities |
| **Success Outcome** | Comprehensive social metrics extraction with 24-hour trend analysis |

## Functional Requirements

| Status | ID | Category | Requirement | Description | Priority | AI Complexity Score |
|--------|----|----|-------------|-------------|----------|--------------------:|
| [ ] | FR-1 | Capability | Extract Current Social Metrics | Retrieve current values for interactions_24h, social_volume_24h, social_dominance, galaxy_score, sentiment, and alt_rank from /coins/list/v2 endpoint | P1 | 4 |
| [ ] | FR-2 | Capability | Extract Historical Social Metrics | Retrieve historical time series data for the same metrics from /coins/{symbol}/time-series/v2 endpoint | P1 | 5 |
| [ ] | FR-3 | Data Processing | Calculate 24-Hour Percentage Changes | Implement calculation formulas to determine 24-hour percentage changes for all applicable metrics | P1 | 6 |
| [ ] | FR-4 | Workflow | Batch Processing | Support processing multiple cryptocurrency symbols in a single request batch | P2 | 5 |
| [ ] | FR-5 | Data Validation | Validate API Responses | Ensure all extracted metrics are within expected ranges and handle missing data | P2 | 3 |

**Category Values**: Capability (core features), Workflow (business processes), Data Validation (input/format rules), UI/UX (interface requirements)
**Priority Values**: P1 (Highest) to P5 (Lowest)
**Constraints**: Embed functional constraints in Description (e.g., "within rate limits", "using only free tier", "without paid libraries")
**Reference**: See [AI Complexity Scoring Framework](../../../assets/artifacts/ai-complexity-scoring-framework.md) for scoring methodology.

### Social Metrics Specification

| Category | Social Metric | Current Value API Call | Rate of Change API Call | Additional Calculation Needed |
|-----------|-------------|---------------------|---------------------|---------------------------|
| Social Engagement | interactions_24h | GET /coins/list/v2 | GET /coins/{symbol}/time-series/v2 | ((current - previous_24h) / previous_24h) * 100 |
| | social_volume_24h | GET /coins/list/v2 | GET /coins/{symbol}/time-series/v2 | ((current_posts_active - previous_24h_posts_active) / previous_24h_posts_active) * 100 |
| | social_dominance | GET /coins/list/v2 | GET /coins/{symbol}/time-series/v2 | ((current_dominance - previous_24h_dominance) / previous_24h_dominance) * 100 |
| Social Quality | galaxy_score | GET /coins/list/v2 | GET /coins/list/v2 | galaxy_score - galaxy_score_previous |
| | sentiment | GET /coins/list/v2 | GET /coins/{symbol}/time-series/v2 | ((current_sentiment - previous_24h_sentiment) / previous_24h_sentiment) * 100 |
| Social Position | alt_rank | GET /coins/list/v2 | GET /coins/list/v2 | alt_rank_previous - alt_rank |

## Technical Requirements

| Status | Category | Requirement | Description | Target/Threshold | AI Complexity Score |
|--------|----------|-------------|-------------|------------------|--------------------:|
| [ ] | Performance | API Rate Limit Management | Stay within $30 plan API limits (500 requests/day) | Maximum 500 requests/day | 4 |
| [ ] | Performance | Response Time | Complete extraction within 30 seconds for 50 assets | <30 seconds for 50 assets | 5 |
| [ ] | Reliability | Error Handling | Graceful handling of API failures and rate limits | 99% success rate with retries | 6 |
| [ ] | Data Processing | Percentage Change Calculation | Accurate calculation of 24-hour percentage changes | 100% accuracy in calculations | 5 |
| [ ] | Data Storage | Metric Caching | Cache current values for 5 minutes to reduce API calls | 5-minute cache duration | 4 |
| [ ] | Privacy | API Key Security | Secure storage and usage of LunarCrush API credentials | Encrypted storage | 3 |
| [ ] | Security | AWS Lambda Deployment | Deploy extraction logic as serverless Lambda function | Lambda function with Python 3.9+ runtime | 5 |
| [ ] | Data Storage | S3 Storage for JSON Files | Store extracted metrics as JSON files in S3 bucket | Organized by date/symbol with proper naming | 4 |
| [ ] | Security | Environment Variables Configuration | Configure API keys and settings via Lambda environment variables | Secure parameter store integration | 4 |
| [ ] | Security | IAM Roles and Permissions | Implement least-privilege IAM roles for Lambda and S3 access | Specific permissions for S3 read/write and CloudWatch logs | 5 |
| [ ] | Performance | Lambda Timeout and Memory Settings | Configure appropriate timeout and memory for extraction workload | 5-minute timeout, 512MB minimum memory | 3 |
| [ ] | Data Processing | Docker Containerization | Create Docker image for local development and testing | Multi-stage build with Python base image | 4 |
| [ ] | Data Processing | Docker Compose Setup | Configure docker-compose for local development environment | Include local S3 simulation (MinIO) | 4 |

**Constraints**: Embed technical constraints in Description or Target/Threshold (e.g., "within 512MB memory", "using <$50/month budget", "without external dependencies")
**Reference**: See [AI Complexity Scoring Framework](../../../assets/artifacts/ai-complexity-scoring-framework.md) for scoring methodology.

## Acceptance Criteria

| Status | ID | Given | When | Then | Type | Validates | Priority |
|--------|-----|-------|------|------|----------|-----------|----------|
| [ ] | AC-1 | User has valid API credentials and cryptocurrency symbols | User requests current social metrics for specified symbols | System returns current values for interactions_24h, social_volume_24h, social_dominance, galaxy_score, sentiment, and alt_rank from /coins/list/v2 endpoint | Functional - Happy Path | FR-1 | P1 |
| [ ] | AC-2 | User has valid API credentials and cryptocurrency symbols | User requests historical social metrics for specified symbols | System retrieves time series data from /coins/{symbol}/time-series/v2 endpoint for the past 24 hours | Functional - Happy Path | FR-2 | P1 |
| [ ] | AC-3 | System has current and previous metric values | System processes extracted data | System calculates accurate 24-hour percentage changes for all applicable metrics using formula: ((current - previous) / previous) * 100 | Functional - Happy Path | FR-3 | P1 |
| [ ] | AC-4 | User provides multiple cryptocurrency symbols | User initiates batch extraction | System processes all symbols efficiently within API rate limits | Functional - Happy Path | FR-4 | P2 |
| [ ] | AC-5 | API response contains missing or invalid data | System validates API responses | System handles missing data gracefully and logs validation errors | Functional - Error Handling | FR-5 | P2 |
| [ ] | AC-6 | System approaches daily API limit | System monitors API usage | System implements throttling to stay within 500 requests/day limit | Technical - Performance | TR-1 | P1 |
| [ ] | AC-7 | API service is temporarily unavailable | System attempts API calls | System implements retry logic with exponential backoff | Technical - Reliability | TR-2 | P1 |
| [ ] | AC-8 | User requests metrics for recently processed symbol | System has cached data | System returns cached values if within 5-minute cache window | Technical - Performance | TR-3 | P3 |
| [ ] | AC-9 | Complete extraction workflow | User requests metrics for multiple symbols with historical data | System returns complete dataset with current values and 24-hour percentage changes | Functional - End-to-End | FR-1-4, TR-1-3 | P1 |
| [ ] | AC-10 | Lambda function is deployed with proper configuration | Lambda function is invoked with test event | Lambda function executes successfully within timeout and memory limits | Technical - Security | TR-7 | P1 |
| [ ] | AC-11 | Extraction process completes successfully | Lambda function processes cryptocurrency symbols | System creates properly formatted JSON files in S3 bucket with correct naming convention | Technical - Data Storage | TR-8 | P1 |
| [ ] | AC-12 | Docker environment is set up for local development | Developer runs docker-compose up | All containers start successfully and application is accessible locally | Technical - Data Processing | TR-10 | P1 |
| [ ] | AC-13 | Environment variables are configured | Lambda function or Docker container starts | System loads all required configuration from environment variables without errors | Technical - Security | TR-9 | P1 |
| [ ] | AC-14 | Error occurs during extraction process | Lambda function encounters API failure or timeout | System logs detailed error information to CloudWatch and handles gracefully | Technical - Reliability | TR-11 | P1 |

**Type Values**:
- **Functional**: Happy Path, Failure Scenario, Edge Case, Error Handling, Integration, End-to-End
- **Technical**: Performance, Security, Reliability

**Validates Column**: References FR/TR IDs that this AC validates (e.g., FR-1, TR-3, or FR-1-4 for ranges)

**Priority Values**: P1 (Highest) to P5 (Lowest)

**Acceptance Criteria Coverage Requirements**:
- Each Functional Requirement (FR) must be validated by at least one Acceptance Criterion
- Each Technical Requirement (TR) must be validated by at least one Acceptance Criterion
- Use AC "Then" statements to directly validate FR/TR requirements
- Review "Validates" column to ensure complete FR/TR coverage

## Dependencies & Prerequisites

### Story Dependencies
| Dependency | Type | Impact | Status | Resolution Timeline | Owner |
|------------|------|--------|--------|-------------------|-------|
| LunarCrush API Access | External | Critical | Required | Immediate | Project Team |
| API Key Configuration | Technical | Critical | Required | Immediate | DevOps |

### Technical Dependencies
**Infrastructure Dependencies**: LunarCrush API v4 access, secure credential storage
**Technology Dependencies**: HTTP client library, JSON parsing, caching mechanism
**Development Dependencies**: Python 3.8+, requests library, environment variable management
**Testing Dependencies**: Mock API responses, test cryptocurrency symbols

### Business Dependencies
**Business Approval**: API budget approval for $30/month plan
**Content Dependencies**: List of target cryptocurrency symbols for monitoring
**Process Dependencies**: API usage monitoring and alerting
**Stakeholder Dependencies**: Cryptocurrency analyst team for requirements validation

## Risk Assessment

### Implementation Risks
**Risk 1: API Rate Limit Exceeded**
- **Probability**: Medium
- **Impact**: High
- **Mitigation Strategy**: Implement request throttling and caching mechanisms
- **Contingency Plan**: Upgrade to higher tier plan or implement request queuing

**Risk 2: Incomplete Historical Data**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation Strategy**: Validate data completeness and handle missing time series points
- **Contingency Plan**: Use interpolation for missing data points or extend time range

### Technical Risks
**Technology Risk**: Changes in LunarCrush API response format may break parsing
**Integration Risk**: API authentication failures or credential expiration
**Performance Risk**: Slow API responses affecting user experience
**Security Risk**: Exposure of API credentials in code or logs

## Definition of Done

- [ ] All Functional Requirements (FR) validated
- [ ] All Technical Requirements (TR) validated
- [ ] All Acceptance Criteria (AC) met
- [ ] Stakeholder sign-off obtained

## Changelog
| Date | Author | Summary | Sections Affected | Reason |
|------|--------|---------|------------------|--------|
| 2025-11-09 08:36:00 | Business Analyst | Initial story creation | All sections | Story breakdown and planning |
| 2025-11-09 08:44:00 | Business Analyst | Added AWS Lambda, S3, and Docker requirements | Technical Requirements, Acceptance Criteria | Infrastructure and deployment considerations |
| 2025-11-09 08:47:00 | Business Analyst | Updated template compliance | Technical Requirements, Requirements Clarifications | Ensuring template structure compliance |
| 2025-11-09 08:52:00 | Business Analyst | Removed unnecessary Requirements Clarifications section | Requirements Clarifications | Removed placeholder text as no clarifications are currently needed |