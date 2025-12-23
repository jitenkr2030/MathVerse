# Kubernetes Services

This directory contains service definitions for MathVerse Kubernetes deployment.

## Service Types

- **ClusterIP**: Internal service communication
- **LoadBalancer**: External access
- **NodePort**: Direct node access
- **Ingress**: HTTP/HTTPS routing

## Configuration

- Port mappings
- Service discovery
- Load balancing
- Health checks

## Usage

Services expose deployments internally and externally:

```bash
kubectl apply -f services/
```

## Ingress

Use Ingress controllers for HTTP routing and SSL termination.