# Kubernetes Secrets

This directory contains Secret definitions for MathVerse Kubernetes deployment.

## Secrets

- **database-credentials/**: Database passwords
- **api-keys/**: External API keys
- **ssl-certificates/**: SSL certificates
- **jwt-secrets/**: Authentication secrets

## Security

- Encrypt sensitive data at rest
- Use RBAC for access control
- Rotate secrets regularly
- Audit secret access

## Usage

Create secrets from files or literals:

```bash
kubectl apply -f secrets/
```

## Best Practices

- Never commit secrets to version control
- Use external secret management when possible
- Implement secret rotation policies