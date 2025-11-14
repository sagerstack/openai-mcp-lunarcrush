# Lambda Docker image with Python 3.13
FROM public.ecr.aws/lambda/python:3.13

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install poetry if not present
RUN pip install poetry

# Configure poetry to create virtual environment in /var/task
RUN poetry config virtualenvs.create false

# Copy application code first (excluding poetry files that cause issues)
COPY src/ ./src/
COPY lambda_function.py ./
COPY tests/ ./tests/

# Install dependencies using poetry (without installing the project itself)
RUN poetry install --only main --no-root

# Set the CMD to your handler
CMD ["lambda_function.lambda_handler"]