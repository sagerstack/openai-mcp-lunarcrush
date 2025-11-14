---
name: orchestrate
description: Execute implementation plan to 100% completion using orchestration-state skill, implementation-plan-parser skill, and direct subagent coordination. Parse plan, extract pending tasks, execute python-developer → test-runner → code-quality sequence, mark tasks [x] complete, continue until all tasks completed or loop exhaustion (5 attempts).
parameters:
  - name: plan_path
    description: Path to the implementation plan markdown file to execute
    required: true
    type: string
  - name: app_name
    description: Application name to determine source code location (passed to python-developer)
    required: true
    type: string
  - name: confirmation_mode
    description: Confirmation mode for execution (interactive, parent-confirm, batch, batch-limit)
    required: false
    type: string
    default: interactive
  - name: batch_limit
    description: Number of sub-tasks to execute automatically in batch-limit mode
    required: false
    type: integer
    default: 5
---

# Orchestrate Command

## Purpose
**PRIMARY OBJECTIVE**: Execute implementation plans to 100% completion - marking every task as [x] complete.

**SUCCESS CRITERIA**: All tasks in implementation plan marked [x] completed.
**FAILURE CRITERIA**: Only corrective feedback loop exhaustion (5 attempts per task).

This command directly orchestrates subagents, ensuring relentless execution until every task is completed.

## Logging Requirements

The orchestration command initializes session logging immediately upon execution:

1. Create session directory structure: `.claude/logs/{session_id}/`
2. Initialize `session.json`, `execution.log`, `checkpoints/`, and `subagent-logs/`
3. Log orchestration events in real-time to maintain execution traceability

## Usage

```bash
# Basic mode (interactive)- confirm after each sub-task
/orchestrate docs/requirements/us-hello-impl-plan.md hello-world

# Parent-task confirmation mode - confirm after each parent task
/orchestrate docs/requirements/us-hello-impl-plan.md hello-world --parent-confirm

# Batch mode - run all tasks without confirmation (except on errors)
/orchestrate docs/requirements/us-hello-impl-plan.md hello-world --batch

# Batch-limit mode - run N sub-tasks then prompt for confirmation
/orchestrate docs/requirements/us-hello-impl-plan.md hello-world --batch-limit 10
```

## Parameters

### Core Parameters
- **plan_path** (required): Path to the implementation plan markdown file
- **app_name** (required): Application name to determine source code location (passed to python-developer)

### Confirmation Modes
- **--interactive** (default): Confirm after each sub-task completion
- **--parent-confirm**: Confirm after each parent task completion
- **--batch**: No confirmation except on loop exhaustion or critical errors
- **--batch-limit N**: Execute N sub-tasks automatically, then confirm

## Process Flow

### 1. Session Setup and Logging Initialization
- Validate implementation plan format and structure
- Parse and classify all tasks for intelligent routing
- Initialize consolidated logging directory structure
- Create session state with specified confirmation mode
- Resume from the earliest incomplete task, otherwise start afresh

### 2. Task Execution with Corrective Feedback Loops
- Execute tasks using subagent sequence: python-developer → test-runner → quality-manager
- Each subagent should respond with a structured response of its work done and additional context. Refer to `.\claude\templates\subagent-response` for the exact format
- Use the subagent response to decide the next subagent to call. 
- Track loop attempts and manage error context passing between subagents
- Apply confirmation mode logic for user interaction points
- Detect loop exhaustion and trigger user intervention

### 3. State Management and Progress Tracking
- Update session state in real-time with current task and subagent
- Log orchestration flow events to execution.log
- Create checkpoints after successful task completion
- Collect final outputs from each subagent

### 4. Error Recovery and Loop Management
- Implement intelligent error classification and response strategies
- Track corrective feedback loop attempts with detailed context
- Handle loop exhaustion detection and user notification
- Support recovery from any checkpoint with full context restoration

### 5. Completion Reporting and Analytics
- Generate comprehensive execution report with success metrics
- Provide loop analytics and error pattern analysis
- Update implementation plan with completion status
- Offer recovery options for incomplete sessions

## Corrective Feedback Loop Workflow

### Standard Subagent Sequence
```
python-developer (implementation)
    ↓ Success
test-runner (testing validation)
    ↓ Success
quality-manager (acceptance criteria and code quality validation)
    ↓ Success
TASK COMPLETE
```

### Error Recovery Patterns
- **Test Failure**: python-developer ← test-runner (with error context)
- **Quality Issues**: Restart at python-developer ← quality-manager (with quality context)
- **Deployment Failure**: deployment retry (with deployment context)
- **Loop Exhaustion**: STOP + User Intervention after 5 attempts


## Integration Points
- **Implementation Plan Parser**: Parses and validates implementation plan structure
- **Orchestration State**: Manages consolidated logging and session state
- **Subagents**
    - **Python Developer**: Implements code with TDD and error context
    - **Test Runner**: Validates implementation and reports test failures
    - **Quality Manager**: Validates against acceptance criteria and standards
- **Progress Dashboard**: Provides enhanced analytics with loop patterns


## Orchestration Execution Logic

The /orchestrate command executes using Claude's native framework:

### 1. Session Initialization
- Use **orchestration-state skill** to generate unique session ID and create logging structure
- Initialize session state tracking
- Create logging directories and initial log entries

### 2. Implementation Plan Parsing
- Use **implementation-plan-parser skill** to extract tasks
- Parse task completion status ([ ] vs [x])
- Calculate completion statistics

### 3. Task Execution Loop
For each pending task in sequence:

```
python-developer subagent (implementation) with app_name context
    ↓ if success
test-runner subagent (testing validation)
    ↓ if success
code-quality subagent (acceptance criteria and code quality validation)
    ↓ if success
Mark task [x] completed in implementation plan
    ↓ continue to next task
```

**Note**: The `app_name` parameter is passed to the python-developer subagent to determine the source code location (e.g., `src/{app_name}/`)

### 4. Error Recovery
- Failed validation → retry with python-developer (max 5 attempts)
- Loop exhaustion → stop execution entirely
- Only valid failure condition: 5 corrective attempts exhausted

### 5. Success Criteria
- **SUCCESS**: All tasks marked [x] in implementation plan
- **FAILURE**: Loop exhaustion on any task
- **NO PREMATURE EXIT**: Continue until 100% completion

### Native Tool Usage
- **Read**: Parse implementation plan
- **Write/Edit**: Update task completion markers
- **Task**: Call specialist subagents
- **Skill**: Use orchestration-state, implementation-plan-parser
- **Bash**: Create directory structure for logging

### Execution Rules

1. **NO PREMATURE EXIT**: Continue until all tasks are [x]
2. **ONLY FAILURE CONDITION**: 5 corrective feedback loop attempts exhausted
3. **REAL-TIME UPDATES**: Mark tasks [x] immediately upon completion
4. **DIRECT SUBAGENT CALLS**: No middleman, direct coordination
5. **RELENTLESS EXECUTION**: Focus solely on 100% completion