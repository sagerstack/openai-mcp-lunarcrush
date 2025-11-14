# Task Executor Test Workflow

## Test Scenarios

This document defines comprehensive test scenarios for the task-executor subagent with corrective feedback loops, confirmation modes, and consolidated logging.

## Test Configuration

### Test Session Setup
```bash
# Test Implementation Plan
TEST_PLAN="docs/requirements/us-hello-impl-plan.md"

# Test Session ID
SESSION_ID="test-enhanced-task-executor"

# Test Logging Directory
LOGS_DIR=".claude/logs/${SESSION_ID}/"
```

## Test Scenario 1: Basic Corrective Feedback Loop

### Objective
Validate the standard `python-developer → test-runner → code-quality` workflow with error recovery.

### Test Steps
```bash
# Initialize session with interactive mode
/orchestrate ${TEST_PLAN} --session-id ${SESSION_ID} --confirmation-mode interactive

# Expected behavior:
# 1. Session created in .claude/logs/test-enhanced-task-executor/
# 2. Start with task 1.2 (resume from current checkpoint)
# 3. Execute python-developer subagent
# 4. Execute test-runner subagent
# 5. Execute code-quality subagent
# 6. Mark task as complete and create checkpoint
# 7. Prompt for user confirmation (interactive mode)
```

### Validation Checks
- ✅ Session directory created with correct structure
- ✅ session.json contains correct confirmation mode
- ✅ execution.log shows subagent handoffs
- ✅ Subagent outputs saved in subagent-logs/
- ✅ Checkpoint created on task completion
- ✅ User confirmation prompted

## Test Scenario 2: Loop Exhaustion Detection

### Objective
Test loop exhaustion after 5 corrective feedback attempts.

### Test Setup
Create a synthetic failing task that will trigger repeated failures.

### Test Steps
```python
# Simulate task that fails consistently
def create_failing_task():
    # Modify implementation plan to include failing test
    # Task will fail test-runner repeatedly
    # Should trigger loop exhaustion after 5 attempts
```

### Expected Behavior
1. **Loop 1-5**: python-developer → test-runner (failure) → python-developer (retry)
2. **Loop 6**: Loop exhaustion detected and execution stopped
3. **User Prompt**: Detailed error analysis with recovery options
4. **Session State**: Set to "loop_exhaustion"

### Validation Checks
- ✅ Loop attempts tracked in session.json
- ✅ Corrective feedback loops logged in execution.log
- ✅ Loop exhaustion analysis saved
- ✅ User intervention prompted with context
- ✅ Recovery options provided

## Test Scenario 3: Batch Mode Execution

### Objective
Validate automatic execution without user confirmation until completion or error.

### Test Steps
```bash
# Start new session in batch mode
SESSION_ID_BATCH="test-batch-mode"
/orchestrate ${TEST_PLAN} --session-id ${SESSION_ID_BATCH} --confirmation-mode batch

# Expected behavior:
# 1. Execute tasks automatically without prompts
# 2. Continue through multiple tasks
# 3. Only stop on critical error or completion
# 4. Handle corrective loops automatically (up to 5 attempts)
```

### Validation Checks
- ✅ No user prompts during execution
- ✅ Automatic corrective feedback loops
- ✅ Loop exhaustion triggers stop (not prompt)
- ✅ Complete execution trace in logs
- ✅ Final completion report generated

## Test Scenario 4: Parent-Task Confirmation

### Objective
Validate confirmation only after parent task completion (not subtasks).

### Test Steps
```bash
# Test with parent-task confirmation mode
SESSION_ID_PARENT="test-parent-confirm"
/orchestrate ${TEST_PLAN} --session-id ${SESSION_ID_PARENT} --confirmation-mode parent-confirm

# Expected behavior:
# 1. Execute subtasks 1.1, 1.2, 1.3, 1.4 automatically
# 2. Prompt after completing parent task 1.0
# 3. Continue to next parent task after confirmation
```

### Validation Checks
- ✅ No prompts for subtasks (1.1-1.4)
- ✅ Prompt generated after parent task 1.0 completion
- ✅ Batch execution within parent task boundaries
- ✅ Confirmation count matches parent task count

## Test Scenario 5: Batch-Limit Mode

### Objective
Validate execution with N tasks then confirmation prompt.

### Test Steps
```bash
# Test batch-limit mode with limit of 3
SESSION_ID_LIMIT="test-batch-limit"
/orchestrate ${TEST_PLAN} --session-id ${SESSION_ID_LIMIT} --confirmation-mode batch-limit --batch-limit 3

# Expected behavior:
# 1. Execute 3 tasks automatically
# 2. Prompt for confirmation after 3 tasks
# 3. Continue next 3 tasks after confirmation
```

### Validation Checks
- ✅ Automatic execution for first 3 tasks
- ✅ Confirmation prompt after batch limit reached
- ✅ Counter resets after confirmation
- ✅ Consistent batch size throughout execution

## Test Scenario 6: Consolidated Logging Validation

### Objective
Validate complete consolidated logging structure and data integrity.

### Expected File Structure
```
.claude/logs/{session-id}/
├── session.json              # Complete session state
├── execution.log             # Chronological execution events
├── checkpoints/              # Task completion records
│   ├── checkpoint-1.1-completed.json
│   ├── checkpoint-1.2-completed.json
│   └── ...
└── subagent-logs/            # Final subagent outputs
    ├── python-developer.json
    ├── test-runner.json
    ├── deployment.json
    └── code-quality.json
```

### Validation Checks
- ✅ All directories created correctly
- ✅ session.json contains comprehensive state
- ✅ execution.log contains JSON lines with timestamps
- ✅ Checkpoints have complete verification results
- ✅ Subagent logs contain "what was done" vs "what is missing"
- ✅ All files are valid JSON with correct schema

## Test Scenario 7: Error Context Passing

### Objective
Validate detailed error context passing between subagents.

### Test Steps
```python
# Create task that will fail with specific errors
def test_error_context():
    # 1. python-developer creates code with syntax error
    # 2. test-runner reports specific test failures
    # 3. python-developer receives detailed error context
    # 4. Validate context contains specific failure information
```

### Validation Checks
- ✅ Error context includes triggering subagent
- ✅ Error details preserved across handoffs
- ✅ Specific failure information passed to recovery subagent
- ✅ Context built correctly for each error type
- ✅ Previous outputs available for recovery

## Test Scenario 8: Recovery and Resume

### Objective
Validate session recovery from checkpoints and loop exhaustion.

### Test Steps
```bash
# 1. Start session and execute several tasks
/orchestrate ${TEST_PLAN} --session-id recovery-test

# 2. Interrupt session (simulate failure)
# 3. Resume from last checkpoint
/resume-orchestration recovery-test

# 4. Resume from loop exhaustion point
/resume-orchestration recovery-test --recovery-point loop-exhaustion-1.2

# 5. Resume with different confirmation mode
/resume-orchestration recovery-test --confirmation-mode interactive
```

### Validation Checks
- ✅ Session state restored correctly
- ✅ Execution history preserved
- ✅ Loop context available for recovery
- ✅ Confirmation mode override works
- ✅ Recovery analysis provided

## Test Scenario 9: Manual Task Handling

### Objective
Validate handling of manual tasks marked `[MANUAL]` in implementation plan.

### Test Steps
```markdown
# Add manual task to implementation plan
- [ ] **[15.0][MANUAL] External Service Configuration**
  - [ ] [MANUAL] Configure external API credentials
  - [ ] [MANUAL] Set up production database
```

### Expected Behavior
- ✅ Automatic stop at manual task regardless of confirmation mode
- ✅ Detailed manual task instructions provided
- ✅ User can mark manual task as complete
- ✅ Execution continues after manual completion

## Test Scenario 10: Performance Validation

### Objective
Validate performance with larger implementation plans and complex scenarios.

### Test Steps
```bash
# Test with plan containing 50+ tasks
# Measure:
# - Session initialization time
# - Task execution speed
# - Logging performance
# - Memory usage
# - File I/O efficiency
```

### Performance Targets
- ✅ Session initialization < 5 seconds
- ✅ Average task execution < 30 seconds
- ✅ Logging overhead < 10% of execution time
- ✅ Memory usage grows linearly with task count
- ✅ File operations don't block execution

## Automated Test Suite

### Test Runner Script
```python
#!/usr/bin/env python3
"""
Automated test suite for enhanced task-executor
"""

def run_all_tests():
    test_scenarios = [
        test_basic_corrective_loop,
        test_loop_exhaustion,
        test_batch_mode,
        test_parent_confirmation,
        test_batch_limit_mode,
        test_consolidated_logging,
        test_error_context_passing,
        test_recovery_resume,
        test_manual_task_handling,
        test_performance_validation
    ]

    results = {}
    for test in test_scenarios:
        try:
            result = test()
            results[test.__name__] = {"status": "PASS", "result": result}
        except Exception as e:
            results[test.__name__] = {"status": "FAIL", "error": str(e)}

    return results

if __name__ == "__main__":
    results = run_all_tests()
    print_test_results(results)
```

### Validation Report
```markdown
# Task Executor Test Results

## Summary
- Total Tests: 10
- Passed: X
- Failed: Y
- Success Rate: Z%

## Detailed Results
| Test | Status | Details |
|------|--------|---------|
| Basic Corrective Loop | PASS | ✅ All subagents executed correctly |
| Loop Exhaustion | PASS | ✅ Detected after 5 attempts |
| Batch Mode | PASS | ✅ No user prompts |
| ... | ... | ... |

## Issues Found
[Document any issues and recommended fixes]
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Task Executor Tests
on: [push, pull_request]
jobs:
  test-task-executor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Run Task Executor Tests
        run: python test_task_executor.py
      - name: Validate Logging Structure
        run: python validate_logging_structure.py
```

This comprehensive test suite validates all aspects of the enhanced task-executor subagent and ensures production readiness.