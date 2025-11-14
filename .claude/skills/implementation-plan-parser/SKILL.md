---
name: implementation-plan-parser
description: Parse markdown implementation plans following the template format, extract task hierarchy, classify tasks for intelligent routing, and validate plan completeness for TDD orchestration.
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Implementation Plan Parser Skill

## Purpose
Parse markdown implementation plans that follow the established template format, extract task hierarchy and dependencies, classify tasks for intelligent routing by the Task Executor, and validate plan completeness for TDD orchestration.

## Input Requirements
- Implementation plan file path (markdown format)
- Plan follows the implementation plan template structure
- Tasks are numbered using the established format [X.Y][CATEGORY]
- Plan includes metadata, requirements coverage, and task sections

## Output Format
Structured task objects with:
- Task identification (number, title, category)
- Task type classification for routing
- Dependencies and execution order
- Task metadata and requirements
- Validation results and completeness metrics

## Process
1. **Plan Loading**: Load and parse the markdown implementation plan
2. **Structure Validation**: Validate plan follows template structure
3. **Task Extraction**: Extract all tasks with metadata and hierarchy
4. **Task Classification**: Classify each task by type for routing
5. **Dependency Analysis**: Analyze task dependencies and execution order
6. **Completeness Validation**: Validate plan completeness and coverage
7. **Output Generation**: Generate structured output for orchestration

## Integration Points
- **Orchestration State Skill**: Stores parsing results and state
- **Progress Dashboard Skill**: Provides task analytics and metrics
- **Solution Architect**: Uses parsing results for plan optimization