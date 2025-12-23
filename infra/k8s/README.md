# Kubernetes Configuration

This directory contains Kubernetes manifests for deploying MathVerse.

## Structure

- **namespaces/**: Namespace definitions
- **deployments/**: Service deployment manifests
- **services/**: Service exposure configurations
- **configmaps/**: Configuration data
- **secrets/**: Sensitive data management

## Usage

```bash
kubectl apply -f namespaces/
kubectl apply -f deployments/
kubectl apply -f services/
```

## Environment-Specific

Create separate directories for different environments (dev, staging, prod).