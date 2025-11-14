# Clean Architecture Code Structure Reference

This document outlines the standard code structure for new Python projects, incorporating Clean Architecture, Domain-Driven Design, and Command-Query Responsibility Segregation (CQRS).

**Key Principles:**
- Each domain entity, class, or value object should be represented in its own file. Do not package them together in a single `model.py`.
- The aggregate root should be represented by the folder name, and related classes should reside within that folder in separate `.py` files.
- Use case files should be explicitly named for their content (e.g., `create_product_command.py`).

```text
.
├── src/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── orm.py
│   │   ├── repository.py       # Concrete implementation of repository interfaces
│   │   └── unit_of_work.py     # Concrete implementation of the UoW interface
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── order/
│   │   │   ├── __init__.py
│   │   │   ├── order.py          # The Order aggregate root class
│   │   │   ├── order_line.py     # A Value Object related to the Order
│   │   │   └── i_order_repository.py # Abstract interface for Order persistence
│   │   └── product/
│   │       ├── __init__.py
│   │       ├── product.py        # The Product aggregate root class
│   │       └── i_product_repository.py # Abstract interface for Product persistence
│   │
│   ├── entrypoints/
│   │   ├── __init__.py
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── order_controller.py   # FastAPI APIRouter for Order endpoints
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── order_schemas.py      # Pydantic schemas for Order API
│   │   └── fastapi_app.py            # Main FastAPI application instance
│   │
│   ├── shared_kernel/
│   │   ├── __init__.py
│   │   └── user.py             # Example of a common domain entity (e.g., User)
│   │
│   └── use_cases/
│       ├── __init__.py
│       ├── commands/
│       │   ├── __init__.py
│       │   └── create_product/
│       │       ├── __init__.py
│       │       ├── create_product_command.py
│       │       └── create_product_handler.py
│       ├── queries/
│       │   ├── __init__.py
│       │   └── get_product_by_sku/
│       │       ├── __init__.py
│       │       ├── get_product_handler.py
│       │       └── get_product_query.py
│       └── i_unit_of_work.py         # Abstract interface for transaction management
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/                 # For testing isolated components (e.g., domain models)
│   ├── integration/          # For testing component interactions (e.g., use cases with a DB)
│   └── e2e/                  # For testing the full application via its API
│
├── .dockerignore             # Specifies files to exclude from the Docker image
├── .gitignore                # Specifies files for Git to ignore
├── docker-compose.yml        # Defines and runs multi-container Docker applications
├── Dockerfile                # Defines the steps to build the application's Docker image
├── pyproject.toml            # Poetry configuration for dependencies and project settings
└── README.md                 # Project documentation
``` 