# Python Developer Subagent Documentation

## Purpose
The Python Developer subagent implements code following Test-Driven Development principles and Clean Architecture patterns.

## TDD Implementation Process

### Test-First Development
1. **Read Failing Tests**: Examine failing tests to understand requirements
2. **Minimal Implementation**: Write smallest code possible to make tests pass
3. **Red-Green-Refactor**: Follow strict TDD cycle
4. **No Gold Plating**: Only implement what tests require
5. **Incremental Development**: Implement one test case at a time

### Clean Architecture Implementation
- **Domain Layer**: Business entities and rules, no external dependencies
- **Use Cases Layer**: Application-specific business rules
- **Infrastructure Layer**: External concerns (database, APIs, UI)
- **Interface Adapters**: Convert data between layers
- **Frameworks & Drivers**: Web frameworks, databases, external interfaces

## Poetry Commands

### Essential Commands
- `poetry run python script.py` - Run Python scripts
- `poetry add package-name` - Add production dependencies
- `poetry add --group dev package-name` - Add development dependencies
- `poetry install` - Install all dependencies
- `poetry shell` - Activate virtual environment

### Project Structure Creation
```bash
mkdir -p src/{app-name}/{domain,use_cases,infrastructure,shared_kernel}
```

## Code Quality Standards

### Type Annotations
```python
from typing import List, Optional, Dict, Any

def process_data(
    input_data: List[str],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process input data with optional configuration."""
    pass
```

### Error Handling
```python
class CustomError(Exception):
    """Custom exception for specific domain errors."""
    pass

def risky_operation() -> bool:
    try:
        # operation logic
        return True
    except SpecificError as e:
        logger.error(f"Operation failed: {e}")
        raise CustomError("Detailed error message") from e
```

### Clean Architecture Example
```python
# Domain Layer
class Entity:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

# Use Case Layer
class UseCase:
    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    def execute(self, entity_id: str) -> Entity:
        return self.repository.find_by_id(entity_id)

# Infrastructure Layer
class Repository:
    def find_by_id(self, entity_id: str) -> Entity:
        # Database/API implementation
        pass
```

## Integration with Other Subagents

### With Test Runner
- Receive failing test scenarios
- Implement code to satisfy tests
- Report implementation status and any blockers

### With Code Quality
- Ensure code meets quality standards before handoff
- Follow coding standards expected by Code Quality
- Provide adequate documentation for review

## Error Handling Strategies

### Common Issues
1. **Import Errors**: Check file structure and __init__.py files
2. **Type Errors**: Add proper type annotations
3. **Test Failures**: Debug and fix implementation issues
4. **Dependency Issues**: Use Poetry to resolve conflicts

### Recovery Process
1. Identify root cause of errors
2. Fix specific issues incrementally
3. Run tests to validate fixes
4. Refactor code while maintaining functionality