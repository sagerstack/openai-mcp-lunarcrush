# Deployment Subagent Documentation

## Purpose
The Deployment subagent handles secure, reliable deployment processes following DevOps best practices.

## Git Workflow

### Feature Branch Process
```bash
# Create feature branch
git checkout -b feature/task-description

# Make changes and commit
git add .
git commit -m "feat: implement new feature with proper description"

# Push and create PR
git push origin feature/task-description
# Create pull request with detailed description
```

### Conventional Commit Format
```
type(scope): description

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Branch Protection
- Never push directly to main branch
- All changes require pull request
- Require code review before merging
- Maintain clean, linear history

## Security Best Practices

### Secrets Management
```bash
# Use environment variables
export API_KEY="your-api-key"

# In Python
import os
api_key = os.getenv("API_KEY")
```

### AWS Security
- Use least privilege IAM policies
- Enable encryption for sensitive data
- Configure security groups properly
- Enable AWS CloudTrail for audit logging

### Container Security
```dockerfile
# Use minimal, secure base images
FROM python:3.13-slim

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Health checks
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Docker Deployment

### Multi-stage Builds
```dockerfile
# Build stage
FROM python:3.13 as builder
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --only=main

# Production stage
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "app_name"]
```

### Docker Commands
```bash
# Build image
docker build -t app-name:latest .

# Run container
docker run -p 8000:8000 app-name:latest

# Scan for vulnerabilities
docker scan app-name:latest
```

## AWS Deployment

### Resource Management
```bash
# Tag all resources
aws ec2 create-tags --resources i-123456 --tags Key=Environment,Value=prod

# Monitor costs
aws ce get-cost-and-usage --time-period Start=2023-01-01,End=2023-01-31
```

### IAM Best Practices
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::specific-bucket/*"
    }
  ]
}
```

## Environment Management

### Environment Configuration
```python
# config.py
import os
from typing import Optional

class Config:
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    API_HOST: str = os.getenv("API_HOST", "localhost")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
```

### Environment Files
```bash
# .env.example
DEBUG=false
API_HOST=localhost
API_PORT=8000
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key-here
```

## Deployment Process

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Code quality checks passed
- [ ] Security scans completed
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Backup strategy in place
- [ ] Rollback plan ready

### Deployment Steps
1. **Environment Preparation**
   - Configure target environment
   - Set up monitoring and alerting
   - Prepare rollback capability

2. **Build Phase**
   - Build deployment artifacts
   - Scan for security vulnerabilities
   - Tag artifacts appropriately

3. **Deployment Phase**
   - Deploy to target environment
   - Run health checks
   - Monitor deployment progress

4. **Post-deployment**
   - Validate successful deployment
   - Run smoke tests
   - Update documentation

## Monitoring and Alerting

### Health Checks
```python
# health.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })
```

### Monitoring Setup
- Application performance monitoring (APM)
- Error tracking and alerting
- Resource usage monitoring
- Custom metrics for business logic

## Error Handling and Recovery

### Rollback Procedures
```bash
# Docker rollback
docker stop app-container
docker run -p 8000:8000 app-name:previous-version

# Kubernetes rollback
kubectl rollout undo deployment/app-name
```

### Common Issues
- **Database Migrations**: Failed migration handling
- **Service Dependencies**: External service unavailability
- **Resource Constraints**: CPU/memory limits exceeded
- **Configuration Errors**: Environment variable issues