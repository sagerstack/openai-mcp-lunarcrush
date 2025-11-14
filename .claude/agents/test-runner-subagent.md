# Test Runner Subagent Documentation

## Purpose
The Test Runner subagent validates implementations through comprehensive testing following Test-Driven Development principles.

## TDD Testing Process

### Test-First Approach
1. **Understand Requirements**: Analyze task requirements and acceptance criteria
2. **Review Existing Tests**: Check current test coverage and identify gaps
3. **Write Failing Tests**: Create tests that initially fail
4. **Validate Failures**: Ensure tests fail for expected reasons
5. **Report Results**: Return test results and failure details to orchestrator

### Test Categories

#### Unit Tests
- Test individual functions and methods in isolation
- Use mocks for external dependencies
- Execute in milliseconds
- Cover all code paths and edge cases

#### Integration Tests
- Test component interactions
- Use real dependencies where possible
- Test with realistic configurations
- Include failure scenarios

#### End-to-End Tests
- Test complete user workflows
- Use real external services and APIs
- Include performance assertions
- Execute in containerized environments

#### Live Environment Tests
- Use actual production-like APIs
- Test with real environment configuration
- Validate real data structures and responses
- Monitor performance in real-world conditions

## Pytest Usage

### Essential Commands
```bash
poetry run pytest                    # Run all tests
poetry run pytest -v                # Verbose output
poetry run pytest --cov=src          # Coverage report
poetry run pytest -m "unit"          # Run specific marker
poetry run pytest --cov-report=html  # HTML coverage report
```

### Test Structure
```python
# tests/test_example.py
import pytest
from src.app_name.module import function_to_test

class TestFunctionToTest:
    def test_happy_path(self):
        """Test normal operation."""
        result = function_to_test(valid_input)
        assert result == expected_output

    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ExpectedError):
            function_to_test(invalid_input)

    @pytest.mark.integration
    def test_integration(self):
        """Test integration with external services."""
        pass
```

### Fixtures Usage
```python
@pytest.fixture
def sample_data():
    return {"key": "value", "number": 42}

@pytest.fixture
def mock_external_api(mocker):
    return mocker.patch('src.app_name.external_api')
```

## Acceptance Criteria Testing

### E2E Test Implementation
- Execute exact E2E test commands from implementation plan
- Validate each AC has corresponding working tests
- Ensure CLI functionality matches expected behavior
- Test error scenarios and help functionality

### Example E2E Test Execution
```bash
# From implementation plan
output=$(poetry run python -m hello_world "Custom message" 2>&1)
echo "$output" | grep -q "Custom message" || exit 1
```

## Coverage Requirements

### Coverage Standards
- **Statement Coverage**: 100% as specified
- **Branch Coverage**: All code branches tested
- **Function Coverage**: All functions tested
- **AC Coverage**: All acceptance criteria validated

### Coverage Analysis
```bash
poetry run pytest --cov=src --cov-report=term-missing
poetry run pytest --cov=src --cov-report=html
```

## Error Handling

### Test Failure Analysis
1. **Root Cause Analysis**: Identify why tests fail
2. **Categorization**: Group failures by type and severity
3. **Fix Recommendations**: Provide specific guidance
4. **Regression Prevention**: Implement measures to prevent regressions

### Common Test Issues
- **Flaky Tests**: Non-deterministic test results
- **Slow Tests**: Performance bottlenecks in tests
- **Test Isolation**: Tests interfering with each other
- **Mock Issues**: Incorrect mock configurations

## Integration with Other Subagents

### With Python Developer (via Orchestrator)
- Test results are passed to Python Developer through the orchestrator
- Failure details guide Python Developer's implementation fixes
- No direct communication - all coordination through Claude

### With Code Quality
- Provide coverage reports for quality assessment
- Ensure tests meet quality standards
- Share performance test results
- Support quality gate processes