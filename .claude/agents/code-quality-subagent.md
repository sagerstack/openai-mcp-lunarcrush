# Code Quality Subagent Documentation

## Purpose
The code-quality subagent validates that all code meets established quality standards and implementation plan requirements.

## Detailed Validation Process

### Project Structure Compliance
- Compare actual directory structure against implementation plan specifications
- Validate Clean Architecture layer separation
- Check file naming conventions and organization
- Verify Poetry configuration matches plan requirements

### Acceptance Criteria Compliance
- Execute E2E tests from implementation plan exactly as written
- Validate each acceptance criteria has corresponding working tests
- Check that implementation fulfills all AC requirements
- Confirm CLI functionality matches expected behavior

### Formatting and Linting Compliance
- **Black**: Run `black --check src/` with line length 88
- **Flake8**: Run `flake8 src/` with complexity limits and naming conventions
- **Pre-commit**: Validate pre-commit hooks configuration
- Ensure zero formatting/linting errors

### Static Code Analysis and Type Safety
- **MyPy**: Run `mypy src/` in strict mode
- Validate 100% type annotation coverage
- Check for type safety violations
- Ensure proper import organization

### Test Coverage Compliance
- **Coverage**: Run `pytest --cov=src --cov-report=html`
- Validate 100% test coverage threshold
- Check test structure mirrors source code structure
- Verify test quality and completeness

### Deployment Compliance
- Validate Poetry scripts are properly configured
- Check environment configuration completeness
- Validate security requirements are met
- Ensure production readiness

### Documentation Standards
- **README**: Validate comprehensive setup and usage instructions
- **Inline docs**: Check docstring coverage on all public APIs
- **Type hints**: Ensure complete type annotation coverage
- **Architecture docs**: Validate Clean Architecture documentation

## Error Reporting
When validation fails, provide:
1. Category of failure
2. Specific files/lines affected
3. Exact error messages
4. Recommended fix actions
5. Commands to re-validate after fixes

## Success Criteria
All validation categories pass with zero failures, enabling task completion marking.