---
name: progress-dashboard
description: Generate real-time progress reports, display task completion status, show test results and quality metrics, and provide execution analytics for implementation plan orchestration.
allowed-tools: Read, Write, Edit, Bash
---

# Progress Dashboard Skill

## Purpose
Generate real-time progress reports and dashboards for implementation plan orchestration. Display task completion status, show test results and quality metrics, and provide comprehensive execution analytics for monitoring and reporting.

## Input Requirements
- Orchestration session identifier
- Execution state and progress data
- Task completion results and metrics
- Quality gate results and test outcomes

## Output Format
Visual dashboard data with:
- Task completion progress and status
- Test results and coverage metrics
- Quality gate compliance status
- Execution timeline and performance
- Analytics and insights

## Process
1. **Data Collection**: Collect execution state and progress data
2. **Metrics Calculation**: Calculate progress metrics and analytics
3. **Dashboard Generation**: Generate visual dashboard representations
4. **Status Reporting**: Provide status updates and alerts
5. **Analytics Processing**: Process execution analytics and insights
6. **Report Generation**: Generate comprehensive progress reports
7. **Alert Management**: Manage alerts and notifications

## Integration Points
- **Orchestration State Skill**: Consumes state data for dashboard
- **Task Executor Subagent**: Receives progress reports
- **Test Runner Subagent**: Displays test results and coverage
- **Code Quality Subagent**: Shows quality gate status
- **Stakeholder Communication**: Provides external reporting