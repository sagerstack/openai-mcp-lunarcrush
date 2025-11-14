# Python Developer Rules

## Implementation Requirements

### Project Structure
- All code must be written under `{project-root}/src/{app-name}/` folder
- Follow Clean Architecture principles for layer separation
- Create proper `__init__.py` files for all packages

### Development Standards
- Follow Test-Driven Development (TDD) principles
- Always use Poetry for all Python execution (`poetry run python` instead of `python`)
- Add type annotations for all function parameters and return values
- Write clear docstrings for all public functions and classes

### Dependencies
- Use `poetry add package-name` for new dependencies
- Use `poetry add --group dev` for development dependencies
- Always use Poetry for dependency management and virtual environment

### Code Quality
- Follow PEP 8 style guide
- Keep functions under 20 lines when possible
- Implement proper exception handling with specific exception types
- Use clear, descriptive naming conventions

## Process

1. Read and understand task requirements
2. Examine existing code structure
3. Write minimal code to satisfy requirements
4. Use Poetry for all Python commands
5. Test implementation immediately
6. Ensure Clean Architecture compliance