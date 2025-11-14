# Error Classification Framework

## Purpose

Define comprehensive error taxonomy for the orchestration system, categorizing errors by severity and determining appropriate response strategies for each error type.

## Error Severity Classification

### Critical Errors (STOP EXECUTION)

#### Syntax & Compilation Errors
**Description**: Code that fails to parse, compile, or execute
**Examples**:
- Python syntax errors (`SyntaxError`, `IndentationError`)
- Import errors (`ModuleNotFoundError`, `ImportError`)
- Type errors that prevent execution
**Response**: Immediate feedback loop to python-developer

#### Test Failures
**Description**: Any failing unit, integration, or E2E test
**Examples**:
- `AssertionError` in test assertions
- Test suite exit code ≠ 0
- Coverage below 0% (no coverage)
**Response**: Immediate feedback loop to python-developer with test context

#### Non-Zero Exit Codes
**Description**: Commands returning failure status
**Examples**:
- `black --check` exit code 1 (formatting issues)
- `flake8` exit code 1 (linting violations)
- `mypy` exit code 1 (type checking failures)
- Poetry/CLI command failures
**Response**: Feedback loop to appropriate subagent with error context

#### Missing Dependencies
**Description**: Required tools, packages, or resources not available
**Examples**:
- `Command not found` for required tools
- Package installation failures
- Missing environment variables or configuration files
**Response**: Stop and prompt user for dependency installation

#### File System Errors
**Description**: Inability to create, read, or modify required files
**Examples**:
- Permission denied errors
- Disk space full
- Invalid file paths
**Response**: Stop execution and prompt user for file system issues

#### Loop Exhaustion
**Description**: Same corrective feedback loop triggered > 5 times
**Examples**:
- Test failures recurring after 5+ fix attempts
- Quality checks failing after 5+ implementation attempts
- Deployment failures after 5+ retry attempts
**Response**: Stop execution and require user intervention

### Warning Errors (LOG but CONTINUE in Batch Mode)

#### Code Quality Issues
**Description**: Non-critical violations of coding standards
**Examples**:
- Line length violations (configurable limits)
- Naming convention issues
- Complex code warnings
- Unused imports or variables
**Response**: Log and continue, provide recommendations in final report

#### Coverage Threshold Issues
**Description**: Test coverage below target but above minimum
**Examples**:
- Coverage 75% when target is 80% but minimum is 60%
- Partial coverage of critical paths
**Response**: Log warning, continue execution, note in completion report

#### Optional Dependencies Missing
**Description**: Optional tools or packages not available
**Examples**:
- Optional linting tools not installed
- Documentation generation tools missing
- Development environment tools unavailable
**Response**: Log warning, continue with reduced functionality

### Manual Intervention Required (STOP and PROMPT)

#### Manual Tasks
**Description**: Tasks explicitly marked as requiring human action
**Examples**:
- Tasks marked `[MANUAL]` in implementation plan
- External account setup or configuration
- Architectural decision points requiring human judgment
**Response**: Stop execution, prompt user to complete manual task

#### Infrastructure Decisions
**Description**: Choices that require human preferences or external knowledge
**Examples**:
- Cloud provider selection
- Database technology choices
- API design decisions requiring stakeholder input
**Response**: Stop and prompt for decision

#### External System Integration
**Description**: Setup requiring external service accounts or configuration
**Examples**:
- GitHub repository creation
- CI/CD pipeline configuration
- External API key configuration
**Response**: Stop and prompt user to complete external setup

## Error Context Collection

### Standard Error Context Schema
```json
{
  "error_id": "unique_error_identifier",
  "timestamp": "2025-11-11T19:10:00Z",
  "session_id": "us-hello-session-001",
  "task_id": "1.2",
  "sub_task_id": "1.2.1",
  "triggering_subagent": "test-runner",
  "error_type": "critical",
  "error_category": "test_failure",
  "severity": "high",
  "exit_code": 1,
  "error_message": "AssertionError: Expected 'Hello, World!' but got 'Hello World'",
  "command_executed": "pytest tests/test_message.py -v",
  "stdout": "...",
  "stderr": "...",
  "files_involved": ["tests/test_message.py", "src/hello_world/message.py"],
  "loop_attempt": 1,
  "recommended_action": "fix_message_formatting",
  "context_available": true,
  "auto_recovery_possible": true
}
```

### Context Preservation Strategies
1. **Command Execution Context**: Save exact command, working directory, environment
2. **File State Context**: Snapshot relevant files before and after failure
3. **Subagent Output Context**: Preserve complete stdout/stderr from subagents
4. **Loop History Context**: Track all previous attempts and their outcomes
5. **Dependency Context**: Record system state and available tools

## Error Response Strategies

### Immediate Feedback Loop
**Trigger**: Critical errors that can be automatically fixed
**Flow**: Error detection → context collection → subagent handoff → retry attempt
**Examples**: Test failures, code quality issues, deployment failures

### User Intervention Required
**Trigger**: Errors requiring external action or decisions
**Flow**: Error detection → context collection → user prompt → manual resolution
**Examples**: Missing dependencies, manual tasks, infrastructure decisions

### Graceful Degradation
**Trigger**: Warning errors that don't prevent task completion
**Flow**: Error detection → log warning → continue execution → note in final report
**Examples**: Non-critical code quality issues, optional dependency missing

### Retry with Backoff
**Trigger**: Transient failures that might resolve themselves
**Flow**: Error detection → wait period → retry → exponential backoff → eventual failure
**Examples**: Network timeouts, temporary service unavailability

## Loop Exhaustion Detection

### Loop Counting Rules
1. **Same Error Type**: Count loops only when same error category repeats
2. **Same Task Context**: Reset counter when different task triggers error
3. **Progress Recognition**: Don't count loop if error shows meaningful progress
4. **Context Changes**: Reset counter when error context significantly changes

### Loop Exhaustion Examples

**Valid Loop Counting**:
```
Loop 1: test failure → python-developer fix → test failure (same test)
Loop 2: test failure → python-developer fix → test failure (same test)
Loop 3: test failure → python-developer fix → test failure (same test)
→ Loop Exhaustion after 5 attempts
```

**Counter Reset Examples**:
- Different test fails → reset counter
- Same test but different assertion error → continue counting
- Infrastructure changes between attempts → reset counter

### Exhaustion Response
1. **Final Log Entry**: Document complete loop history
2. **Context Bundle**: Package all error contexts for user review
3. **Stop Execution**: Halt further automatic attempts
4. **User Notification**: Prompt with detailed error summary
5. **Recovery Options**: Offer resume from last successful checkpoint

## Error Analytics and Metrics

### Tracking Metrics
- **Error Frequency**: Count by error type and category
- **Loop Efficiency**: Success rate of corrective feedback loops
- **Recovery Time**: Average time to resolve each error type
- **Subagent Performance**: Success rates by subagent type
- **Task Complexity**: Error rates by task type and complexity

### Reporting Formats
1. **Real-time Dashboards**: Current error status and loop counts
2. **Session Summaries**: Complete error history per orchestration session
3. **Trend Analysis**: Error patterns across multiple sessions
4. **Performance Metrics**: Subagent efficiency and success rates

## Integration with Confirmation Modes

### Interactive Mode
- User notified of every error regardless of severity
- Can choose to continue or intervene at any point
- Full error context always displayed

### Batch Modes
- Automatic error recovery for all recoverable errors
- User only notified on loop exhaustion or manual intervention required
- Error context logged but not displayed during execution

### Parent-Task Confirmation
- Automatic recovery for all errors within parent tasks
- User notified only when parent task cannot complete due to errors
- Comprehensive error summary provided at parent task boundaries

This error classification framework ensures **predictable error handling**, **efficient recovery strategies**, and **comprehensive error tracking** while maintaining **user control** over critical decision points.