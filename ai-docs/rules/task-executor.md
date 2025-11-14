# Task Executor Rules

## Execution Requirements

### Sequential Processing
- Execute tasks one at a time, never in parallel
- Respect task dependencies and execution order
- Complete each task fully before proceeding
- Verify task completion before moving to next task
- Maintain original task order from implementation plan

### Task Routing
- Classify each task by type and requirements
- Route tasks to appropriate subagents based on classification
- For code tasks, always use python-developer → test-runner → code-quality sequence
- Preserve context between subagent interactions

### State Management
- Save state after each successful task completion
- Support resumption from any checkpoint
- Maintain detailed progress information
- Log all execution history and decisions

## Process

1. Parse and analyze implementation plan
2. Classify tasks by type and requirements
3. Execute tasks in sequential order
4. Route to appropriate subagents
5. Verify completion before proceeding
6. Handle errors with appropriate recovery strategies