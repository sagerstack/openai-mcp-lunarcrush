# Corrective Feedback Loop Workflow

## Purpose

Define the orchestration workflow that ensures task completion through automated quality gates and intelligent error recovery using corrective feedback loops.

## Core Workflow Sequence

### Standard Flow: `python-developer → test-runner → deployment (if applicable) → code-quality`

Each task completes through a sequence of specialized subagents, each acting as a quality gate:

1. **Python-Developer**: Implements code following TDD principles
2. **Test-Runner**: Validates implementation with comprehensive test suite
3. **Deployment**: (if applicable) Deploys and validates infrastructure changes
4. **Code-Quality**: Validates against acceptance criteria and coding standards

## Corrective Feedback Loop Logic

### Loop Triggers and Recovery

#### Test Failures
```
test-runner reports failure → python-developer receives error context → reimplementation → test-runner re-runs
```

#### Code Quality Issues
```
code-quality reports non-compliance → restart entire sequence → python-developer with quality feedback → test-runner → deployment → code-quality
```

#### Deployment Failures
```
deployment reports failure → deployment subagent retried with deployment context → continue with next subagents
```

### Loop Exhaustion Definition

**Error occurs when the same corrective feedback loop is triggered more than 5 times** for the same task or sub-task.

#### Loop Counting Examples

**Test Failure Loop**:
- Attempt 1: `test-runner fails` → `python-developer fixes`
- Attempt 2: `test-runner fails` → `python-developer fixes`
- Attempt 3: `test-runner fails` → `python-developer fixes`
- Attempt 4: `test-runner fails` → `python-developer fixes`
- Attempt 5: `test-runner fails` → `python-developer fixes`
- **Attempt 6**: `test-runner fails` → **LOOP EXHAUSTION ERROR**

**Quality Loop**:
- Each full sequence restart counts as one loop attempt
- Loop counter resets when different error type occurs

## Context Passing Between Subagents

### Error Context Format

#### Test Runner → Python Developer
```json
{
  "triggering_subagent": "test-runner",
  "error_type": "test_failure",
  "failed_tests": [
    "test_message.py::test_default_message - AssertionError: Expected 'Hello, World!' but got 'Hello World'",
    "test_message.py::test_custom_message - AttributeError: 'Message' object has no attribute 'format'"
  ],
  "test_results": {
    "total": 5,
    "passed": 3,
    "failed": 2
  },
  "coverage": "60%",
  "what_needs_fixing": ["Message formatting implementation", "Complete test coverage"],
  "loop_attempt": 1
}
```

#### Code Quality → Python Developer (Restart Sequence)
```json
{
  "triggering_subagent": "code-quality",
  "error_type": "quality_non_compliance",
  "quality_check_failures": [
    "flake8: Line too long (92 > 88)",
    "mypy: Missing type hints"
  ],
  "acceptance_criteria_issues": ["criteria_1_2_a - Poetry project not fully configured"],
  "what_needs_fixing": ["Code formatting violations", "Type annotations", "Poetry configuration"],
  "restart_sequence": true,
  "loop_attempt": 1
}
```

#### Deployment → Deployment (Retry)
```json
{
  "triggering_subagent": "deployment",
  "error_type": "deployment_failure",
  "deployment_error": "Docker build failed: Cannot install dependencies",
  "infrastructure_issues": ["Missing Dockerfile", "Invalid poetry.lock"],
  "what_needs_fixing": ["Docker configuration", "Dependency resolution"],
  "retry_only": true,
  "loop_attempt": 1
}
```

## Subagent Coordination Patterns

### Success Handoff Pattern
```
python-developer (success) → test-runner
test-runner (success) → deployment (if applicable) OR code-quality
deployment (success) → code-quality
code-quality (success) → TASK COMPLETE
```

### Failure Recovery Pattern
```
test-runner (failure) → python-developer (with context)
code-quality (failure) → restart sequence at python-developer (with context)
deployment (failure) → deployment retry (with context)
```

### Loop Exhaustion Pattern
```
Loop counter > 5 → ERROR LOG → USER INTERVENTION REQUIRED
```

## Task Types and Workflow Variations

### Code Implementation Tasks
**Sequence**: python-developer → test-runner → code-quality
**No deployment stage** required for pure implementation

### Infrastructure Tasks
**Sequence**: python-developer → test-runner → deployment → code-quality
**Full sequence** with deployment validation

### Documentation Tasks
**Sequence**: python-developer → code-quality
**Simplified sequence** - no testing or deployment

## Intelligent Error Classification

### Critical Errors (Always Trigger Immediate Feedback Loop)
- Syntax/compilation errors
- Test failures (any failing test)
- Deployment failures
- Missing dependencies
- Validation failures

### Quality Errors (Trigger Full Sequence Restart)
- Code quality violations
- Acceptance criteria non-compliance
- Missing implementation requirements

### Manual Intervention Required (Stop and Prompt)
- Tasks marked `[MANUAL]` in implementation plan
- External system configuration needed
- Architectural decisions required

## Logging Requirements

### Execution Log Events
Each subagent transition generates an execution log entry:
```json
{
  "timestamp": "2025-11-11T19:10:00Z",
  "session_id": "us-hello-session-001",
  "task": "1.2",
  "orchestration_event": "subagent_handoff",
  "from_subagent": "test-runner",
  "to_subagent": "python-developer",
  "reason": "corrective_feedback_loop_triggered",
  "loop_count": 1,
  "error_context": {...}
}
```

### Subagent Final Output
Each subagent creates a final output JSON file with completion status:
- **What was done**: Implementation details, test results, deployment status
- **What is missing**: Gaps, failures, non-compliance issues
- **Recommendations**: Specific fixes needed for next attempt

## Integration with Confirmation Modes

### Interactive Mode
- User notified after each corrective loop
- Can intervene at any failure point

### Batch Modes
- Automatic retry up to loop exhaustion (5 attempts)
- User only notified on loop exhaustion or critical system errors

### Parent-Task Confirmation
- Automatic retries within parent tasks
- User notified only when entire parent task completes or fails

This workflow ensures **systematic quality improvement** through iterative refinement while preventing **infinite loops** through intelligent exhaustion detection and user intervention triggers.