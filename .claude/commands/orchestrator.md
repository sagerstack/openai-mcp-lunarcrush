---
description: Execute implementation plan to 100% completion by orchestrating SDLC workflow, delegating tasks and coordinating between subagents. Parse plan, extract pending tasks, execute python-developer → test-runner → code-quality sequence, mark tasks [x] complete, continue until all tasks completed or loop exhaustion (5 attempts).
name: orchestrator
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

## Prime Directive
This is the entry point to initiate AI SDLC workflow using Claude Code's native capabilities. Orchestrator's primary objective is to accept an implementation plan as input, iterate over every task and execute it by delegating to one or more subagent. The orchestrator will complete its workflow when all implementation tasks have been completed.   

## Usage

## Instructions
1. Prioritize precision, attention to detail, accuracy of results, 100% completeness and adherence to instructions over speed of execution
2. Task is defined as either a Parent task, or Sub-task

## Workflow
1. Read the provided implementation plan, one task at a time. Begin at the first outstanding task.
2. If a task is marked as [MANUAL] and incomplete, ask user to complete it and mark it accordingly in the implementation plan.
3. For each task, execute the following steps:
    a.  Initialize loop-counter=0
    b.  Invoke **python-developer** subagent to implement the task. Analyze the response from the subagent. 
    c.  If the python-developer response is failure, 
        (i)     Restart from (a) 
        (ii)    Track loop-counter+1
        (iii)   If loop-counter exceeds 5, stop execution, exit loop
    d.  If the response status is success, invoke **quality-manager** subagent to validate the task completion and accuracy. Analyze the response from the subagent
    e.  If the quality-manager response status is failure, 
        (i)     Restart from (b)
        (ii)
    e.  If the quality-manager response status is success, mark the task as `[x]` (completed) in the implementation plan
    f.  Move to the next task
    e.        


## Logging


## Report



