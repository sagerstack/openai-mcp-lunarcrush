# Response template for Subagents

# When to Use
When the subagent is asked to execute an instruction. After completion, the subagent should provide a final summarized response in this format.

# Response Format
```json
{
    "task-no": "{parent-task-id}-{sub-task-id}", # for e.g. 5-2
    "status":"success" | "failure",
    "msg": "{if developer: provide a summary of the work done, 
             if test-runner: provide a summary of the test results,
             if quality-manager: provide an assessment of the quality of the deliverable}",
    "context":"{provide all the context needed for the next subagent}"
}
```