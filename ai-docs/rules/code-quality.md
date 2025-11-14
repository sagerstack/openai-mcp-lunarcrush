# Code Quality Rules

## Validation Categories

The code-quality subagent must validate these categories:

### 1. Project Structure Compliance
- Verify directory structure matches implementation plan
- Validate file locations are correct
- Check package configuration compliance

### 2. Acceptance Criteria Compliance
- Validate each AC is fulfilled by implementation
- Confirm each AC is validated by successful E2E test run
- Check E2E tests match implementation plan exactly

### 3. Formatting and Linting Compliance
- Run black formatting checks
- Run flake8 linting checks
- Ensure zero formatting/linting errors

### 4. Static Code Analysis and Type Safety Compliance
- Run mypy type checking in strict mode
- Ensure 100% type coverage
- Zero type errors allowed

### 5. Test Coverage Compliance
- Run pytest with coverage reporting
- Ensure 100% test coverage as specified
- Validate test structure matches source code

### 6. Deployment Compliance
- Validate deployment readiness
- Check security compliance
- Verify environment configuration

### 7. Documentation Standards Compliance
- Validate README completeness
- Check inline documentation coverage
- Verify API documentation completeness

## Quality Gates

- All validation categories must pass
- Zero tolerance for failures
- Fail fast on first category failure
- Provide specific failure details for correction

## Process

1. Run validation categories in sequence
2. Stop immediately on any failure
3. Report specific failure details
4. Return success only if all categories pass