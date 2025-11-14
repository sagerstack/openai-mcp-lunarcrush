---
name: orchestration-state
description: Orchestration state management with consolidated logging, corrective feedback loop tracking, and multiple confirmation modes. Manage session state, execution logs, checkpoints, and recovery for TDD-first implementation plan orchestration.
allowed-tools: Read, Write, Edit, Bash
---

# Orchestration State Skill

## Purpose
Manage comprehensive orchestration state including consolidated logging, corrective feedback loop tracking, and multi-mode confirmation support. Provide centralized logging infrastructure, session recovery capabilities, and detailed execution analytics for TDD-first implementation plan orchestration.

## Input Requirements
- Orchestration session identifier and confirmation mode
- Task execution status and loop attempt tracking
- Subagent coordination and context passing data
- Checkpoint data and completion verification
- Execution flow events and error context
- Loop exhaustion detection and user intervention triggers

## Output Format
Consolidated logging structure with:
- **Session State**: Combined session metadata and real-time status
- **Execution Logs**: Detailed orchestration flow and subagent coordination
- **Checkpoint Management**: Task completion records and verification results
- **Subagent Logs**: Final output from each subagent (what was done vs what is missing)
- **Loop Analytics**: Corrective feedback loop tracking and exhaustion detection
- **Progress Metrics**: Completion percentages, success rates, and performance analytics

## Process

### 1. Session Initialization and Logging Setup
- Generate unique session-id in the format `{app-name}-yyyyymmdd-HH24MMss`
- Create consolidated logging directory: `.claude/logs/{session-id}/`
- Initialize session state file with confirmation mode and metadata
- Set up execution log, checkpoint directory, and subagent log directories
- Configure log rotation and retention policies

### 2. Real-time State Management
- Update session state with current task, subagent, and loop counts
- Track corrective feedback loop attempts and context preservation
- Maintain bidirectional sync with implementation plan markdown
- Monitor confirmation mode requirements and user intervention points

### 3. Execution Logging
- Log orchestration flow events (subagent handoffs, loop triggers)
- Record subagent context passing and error recovery attempts
- Track loop exhaustion detection and user intervention requirements
- Maintain chronological execution timeline with timestamps

### 4. Checkpoint and Subagent Log Management
- Create checkpoints after successful task completion
- Collect final outputs from each subagent (what was done vs what is missing)
- Maintain subagent logs in standardized format for debugging
- Enable recovery from any completed checkpoint with full context

### 5. Loop Exhaustion Detection
- Track loop attempts per task and error type
- Detect when same corrective feedback loop exceeds 5 attempts
- Trigger user intervention prompts for loop exhaustion
- Maintain complete loop history for analysis and debugging

### 6. Confirmation Mode Support
- **Interactive Mode**: Prompt after each sub-task completion
- **Parent-Task Confirmation**: Prompt after each parent task completion
- **Batch Mode**: Automatic execution until loop exhaustion or critical error
- **Batch-Limit Mode**: Automatic execution for N sub-tasks then prompt

### 7. Recovery and Resumption
- Enable session recovery from any checkpoint with full context restoration
- Support resume from specific task numbers or loop states
- Maintain complete execution history for debugging and analysis
- Provide analytics on success rates and loop patterns

## File Structure Management

### Consolidated Logging Directory
```
.claude/logs/{session-id}/
├── session.json              # Combined session state (replaces current-session.json + sessions/*.json)
├── execution.log             # Real-time orchestration flow events
└── subagent-logs/            # Final subagent outputs
    ├── python-developer.json # Implementation state and what was done
    ├── test-runner.json      # Test results and what is missing
    ├── deployment.json       # Deployment state and compliance
    └── code-quality.json     # Quality assessment and non-compliance issues
```

### Session State Schema (session.json)
```json
{
  "session_id": "us-hello-session-001",
  "status": "active",
  "confirmation_mode": "interactive",
  "started_at": "2025-11-11T19:00:00Z",
  "implementation_plan": "docs/requirements/us-hello-impl-plan.md",
  "current_task": "1.2",
  "current_subagent": "test-runner",
  "completed_tasks": ["1.1"],
  "failed_tasks": [],
  "loop_attempts": {
    "task-1.2": {
      "current_loop": 1,
      "last_attempt": "2025-11-11T19:10:00Z",
      "error_context": "test_failure"
    }
  },
  "total_tasks": 82,
  "completion_percentage": 1.2,
  "last_completed_subtask_at": "2025-11-11T19:05:00Z",
  "last_completed_task_id": "1.1",
  "user_story_id": "US-HELLO",
}
```

### Execution Log Schema (execution.log)
```json
{"timestamp":"2025-11-11T19:10:00Z","session_id":"us-hello-session-001","task":"1.2","orchestration_event":"subagent_handoff","from_subagent":"python-developer","to_subagent":"test-runner","reason":"implementation_complete","loop_attempt":1}
{"timestamp":"2025-11-11T19:12:00Z","session_id":"us-hello-session-001","task":"1.2","orchestration_event":"corrective_feedback_loop","triggering_subagent":"test-runner","error_type":"test_failure","next_subagent":"python-developer","loop_count":1,"error_context":{"failed_tests":2}}
{"timestamp":"2025-11-11T19:15:00Z","session_id":"us-hello-session-001","task":"1.2","orchestration_event":"task_complete","completed_by":"code-quality","final_status":"success","total_loops":1}
```

## Integration Points
- **Python Developer Subagent**: Error context reception and implementation guidance
- **Test Runner Subagent**: Test failure reporting and detailed error context
- **Deployment Subagent**: Deployment failure reporting and retry coordination
- **Code Quality Subagent**: Non-compliance reporting and acceptance criteria validation
- **Progress Dashboard Skill**: Enhanced analytics with loop patterns and success rates
- **Implementation Plan Parser**: Task structure and completion status synchronization
- **CLI Commands**: Support for all confirmation modes and resume functionality