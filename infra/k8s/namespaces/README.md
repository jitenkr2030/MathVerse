# Kubernetes Namespaces

This directory contains namespace definitions for MathVerse Kubernetes deployment.

## Namespaces

- **mathverse-dev**: Development environment
- **mathverse-staging**: Staging environment
- **mathverse-prod**: Production environment
- **mathverse-monitoring**: Monitoring and logging

## Usage

Apply namespaces before deploying other resources:

```bash
kubectl apply -f namespaces/
```

## Resource Quotas

Each namespace has configured resource limits and quotas.

## Network Policies

Network policies control inter-service communication.