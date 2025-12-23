# Nginx Configuration

This directory contains Nginx reverse proxy configuration for MathVerse.

## Files

- **nginx.conf**: Main Nginx configuration
- **sites/**: Site-specific configurations
- **ssl/**: SSL certificate configurations

## Features

- Load balancing
- SSL termination
- Static file serving
- API gateway
- Rate limiting

## Usage

Configuration is used in Docker containers and Kubernetes deployments.

## Testing

```bash
nginx -t -c nginx.conf
```