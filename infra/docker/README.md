# Docker Configuration

This directory contains Docker configurations for MathVerse services.

## Files

- **nginx/**: Nginx reverse proxy configuration
- **postgres/**: PostgreSQL database configuration
- **redis/**: Redis cache configuration

## Usage

Use `docker-compose.yml` in the root directory to start all services.

## Development

```bash
docker-compose up -d
```

## Production

See individual service directories for production Docker configurations.