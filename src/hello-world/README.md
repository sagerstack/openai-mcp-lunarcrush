# Hello World

A simple console application demonstrating Clean Architecture and TDD principles.

## Installation

```bash
poetry install
```

## Usage

```bash
# Display default message
poetry run hello-world

# Display custom message
poetry run hello-world "Custom message"
```

## Development

```bash
# Run tests
poetry run pytest

# Format code
poetry run black .

# Lint code
poetry run flake8 .

# Type check
poetry run mypy .
```