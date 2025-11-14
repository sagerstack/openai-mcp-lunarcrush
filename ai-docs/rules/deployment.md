# Deployment Rules

## Git Requirements

- Never push directly to main branch
- Always work on feature branches
- Create pull requests for all changes
- Follow conventional commit message format
- Maintain clean, linear git history

## Security Requirements

- Never expose secrets in deployments
- Use environment variables for configuration
- Follow principle of least privilege
- Implement proper access controls
- Maintain audit trail of deployment activities

## Environment Management

- Maintain separate environments (dev, staging, prod)
- Use proper configuration management
- Implement secrets management solutions
- Validate environment configurations before deployment
- Ensure environment parity

## Process

1. Prepare target environment
2. Run pre-deployment validations
3. Build deployment artifacts
4. Execute deployment with rollback capability
5. Validate successful deployment
6. Set up monitoring and alerting