# Kubernetes ConfigMaps

This directory contains ConfigMap definitions for MathVerse Kubernetes deployment.

## ConfigMaps

- **app-config/**: Application configuration
- **nginx-config/**: Nginx configuration
- **database-config/**: Database configuration

## Usage

ConfigMaps provide configuration data to pods:

```bash
kubectl apply -f configmaps/
```

## Environment-Specific

Create separate ConfigMaps for different environments.

## Updates

ConfigMaps can be updated without pod restarts.