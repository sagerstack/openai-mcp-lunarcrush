---
name: resume-orchestration
description: Enhanced resume command for orchestration sessions with consolidated logging, corrective feedback loop recovery, and multiple confirmation modes. Maintains full execution context and state for seamless continuation.
parameters:
  - name: session_id
    description: Session identifier of the orchestration to resume
    required: true
    type: string
  - name: recovery_point
    description: Specific checkpoint, task number, or loop state to resume from (optional, defaults to last checkpoint)
    required: false
    type: string
  - name: force_restart
    description: Force restart from beginning instead of resuming
    required: false
    type: boolean
    default: false
  - name: confirmation_mode
    description: Override confirmation mode for resumed session (interactive, parent-confirm, batch, batch-limit)
    required: false
    type: string
  - name: batch_limit
    description: Override batch limit for resumed session in batch-limit mode
    required: false
    type: integer
  - name: logs_dir
    description: Override logs directory (default: .claude/logs)
    required: false
    type: string
    default: .claude/logs
  - name: recovery_analysis
    description: Show detailed analysis of session failure before resuming
    required: false
    type: boolean
    default: false
---

# Enhanced Resume Orchestration Command

## Purpose
Enhanced resume functionality for orchestration sessions that supports consolidated logging recovery, corrective feedback loop restoration, and flexible confirmation modes. Maintains complete execution context including subagent states, loop attempts, and error context for seamless continuation.

## Enhanced Usage

### Basic Resume Operations
```bash
# Resume from last checkpoint with original settings
/resume-orchestration us-hello-session-001

# Resume from specific checkpoint
/resume-orchestration us-hello-session-001 --recovery-point checkpoint-1.5

# Resume from specific task number
/resume-orchestration us-hello-session-001 --recovery-point task-2.3

# Resume from loop exhaustion point
/resume-orchestration us-hello-session-001 --recovery-point loop-exhaustion-1.2
```

### Recovery Analysis
```bash
# Show detailed failure analysis before resuming
/resume-orchestration us-hello-session-001 --recovery-analysis

# Resume with failure analysis
/resume-orchestration us-hello-session-001 --recovery-point checkpoint-3.2 --recovery-analysis
```

### Confirmation Mode Overrides
```bash
# Resume with different confirmation mode
/resume-orchestration us-hello-session-001 --confirmation-mode batch

# Resume in batch-limit mode with custom limit
/resume-orchestration us-hello-session-001 --confirmation-mode batch-limit --batch-limit 10
```

### Restart Options
```bash
# Force restart from beginning with same session ID
/resume-orchestration us-hello-session-001 --force-restart

# Restart with different confirmation mode
/resume-orchestration us-hello-session-001 --force-restart --confirmation-mode parent-confirm
```

## Parameters

### Core Parameters
- **session_id** (required): Session identifier of the orchestration to resume
- **recovery_point** (optional): Checkpoint, task, or loop state to resume from
- **force_restart** (optional): Force restart from beginning instead of resuming

### Override Parameters
- **--confirmation_mode**: Override original confirmation mode (interactive, parent-confirm, batch, batch-limit)
- **--batch_limit**: Override batch limit for batch-limit mode
- **--logs_dir**: Override logs directory (default: .claude/logs)

### Analysis Parameters
- **--recovery_analysis**: Show detailed analysis of session failure before resuming

## Enhanced Recovery Options

### Checkpoint Recovery
```bash
# Resume from specific completed checkpoint
/resume-orchestration session-001 --recovery-point checkpoint-1.5-completed
```

### Task Recovery
```bash
# Resume from specific task (incomplete or failed)
/resume-orchestration session-001 --recovery-point task-2.3

# Resume from beginning of parent task
/resume-orchestration session-001 --recovery-point parent-task-2.0
```

### Loop Exhaustion Recovery
```bash
# Resume from loop exhaustion point with fresh context
/resume-orchestration session-001 --recovery-point loop-exhaustion-1.2

# Resume with different error recovery strategy
/resume-orchestration session-001 --recovery-point loop-exhaustion-1.2 --confirmation-mode interactive
```

### Subagent State Recovery
```bash
# Resume from specific subagent failure
/resume-orchestration session-001 --recovery-point test-runner-failure-1.2

# Resume with detailed error context
/resume-orchestration session-001 --recovery-point code-quality-non-compliance-3.4
```

## Enhanced Process Flow

### 1. Session Discovery and Validation
- Locate session directory in consolidated logs structure
- Validate session state file and logging integrity
- Check for incomplete checkpoints or corrupted data

### 2. Recovery Point Analysis
- Analyze execution log for failure patterns and loop history
- Identify last successful checkpoint and error context
- Validate recovery point integrity and availability

### 3. Context Restoration
- Restore session state with current task, subagent, and loop counts
- Rebuild error context from subagent logs and execution history
- Restore implementation plan synchronization state

### 4. Enhanced Logging Recovery
- Append to existing execution log with recovery events
- Maintain continuity in subagent log files
- Preserve complete loop history and analytics

### 5. Confirmation Mode Application
- Apply original or overridden confirmation mode settings
- Configure batch limits and user interaction points
- Set up loop exhaustion detection thresholds

### 6. Continuation Execution
- Resume task execution with restored context
- Continue corrective feedback loops with preserved state
- Maintain progress tracking and analytics continuity

## Recovery Analysis Features

### Session State Summary
```json
{
  "session_id": "us-hello-session-001",
  "status": "loop_exhaustion",
  "last_activity": "2025-11-11T19:15:00Z",
  "completion_percentage": 15.2,
  "failed_at_task": "1.2",
  "loop_exhaustion_details": {
    "task": "1.2",
    "error_type": "test_failure",
    "loop_attempts": 6,
    "last_error_context": "2 failing tests"
  }
}
```

### Error Pattern Analysis
- **Loop History**: Complete timeline of all corrective feedback loops
- **Error Frequency**: Most common error types and patterns
- **Subagent Performance**: Success rates by subagent type
- **Recovery Recommendations**: Suggested strategies for successful continuation

### Recovery Recommendations
1. **Change Confirmation Mode**: Switch to interactive for manual intervention
2. **Modify Implementation Strategy**: Alternative approaches for persistent issues
3. **External Dependencies**: Install missing tools or configure environment
4. **Task Skip Option**: Skip problematic tasks with manual completion later

## Consolidated Logging Integration

### Session Directory Structure
```
.claude/logs/us-hello-session-001/
├── session.json              # Session state at time of pause/failure
├── execution.log             # Complete execution history up to failure point
├── checkpoints/              # All completed checkpoints before failure
│   ├── checkpoint-1.1-completed.json
│   └── checkpoint-1.2-completed.json
└── subagent-logs/            # Final outputs from last subagent attempts
    ├── python-developer.json # Last implementation attempt
    ├── test-runner.json      # Failure details and what needs fixing
    ├── code-quality.json     # Quality issues and non-compliance items
    └── loop-exhaustion.json  # Loop exhaustion analysis and context
```

### Recovery Point Validation
- **Checkpoint Integrity**: Verify checkpoint data completeness
- **Context Preservation**: Ensure error context and loop history maintained
- **State Consistency**: Validate session state synchronization with implementation plan
- **Log Continuity**: Ensure execution log can be appended seamlessly

## Integration Points
- **Enhanced Orchestration State**: Loads session state from consolidated structure
- **Enhanced Task Executor**: Continues execution with restored loop context
- **Subagent Coordination**: Restores error context and implementation state
- **Progress Dashboard**: Provides recovery analysis and failure patterns
- **Implementation Plan Parser**: Synchronizes plan completion status

## Example Recovery Scenarios

### Simple Checkpoint Recovery
```bash
# Session failed at task 3.4, last successful checkpoint was 3.1
/resume-orchestration feature-auth-session-001 --recovery-point checkpoint-3.1-completed
# Restores state and continues from task 3.2
```

### Loop Exhaustion Recovery
```bash
# Test failures caused loop exhaustion after 5 attempts
/resume-orchestration feature-auth-session-001 --recovery-analysis
# Shows detailed failure analysis, suggests alternative approach
/resume-orchestration feature-auth-session-001 --confirmation-mode interactive
# Resumes with manual intervention capability
```

### Batch Mode Recovery
```bash
# Session running in batch mode hit critical error
/resume-orchestration feature-auth-session-001 --recovery-point task-5.2 --confirmation-mode parent-confirm
# Resumes with more conservative confirmation mode
```

### Full Restart with Context
```bash
# Restart from beginning but keep learning from failures
/resume-orchestration feature-auth-session-001 --force-restart --recovery-analysis
# Uses failure patterns to avoid repeated mistakes
```