# Kubernetes Deployments

This directory contains deployment manifests for MathVerse services.

## Services

- **backend/**: API service deployment
- **frontend/**: Web application deployment
- **database/**: Database deployment
- **cache/**: Redis cache deployment

## Configuration

- Resource limits and requests
- Health checks
- Environment variables
- Volume mounts

## Usage

Deploy services individually:

```bash
kubectl apply -f deployments/backend/
kubectl apply -f deployments/frontend/
```

## Scaling

Use HPA (Horizontal Pod Autoscaler) for automatic scaling.