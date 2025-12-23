# Recommendation Engine Configuration

This directory contains configuration files for the recommendation engine service.

## Files

- **development.yaml**: Development environment config
- **production.yaml**: Production environment config
- **test.yaml**: Test environment config
- **model-config.yaml**: Machine learning model configuration
- **logging.yaml**: Logging configuration
- **database.yaml**: Database connection settings

## Configuration

### Model Settings
- Algorithm selection
- Hyperparameters
- Training parameters
- Feature engineering settings

### Performance
- Caching configuration
- Batch processing settings
- Memory limits
- Timeout settings

### Data Sources
- Database connections
- External API endpoints
- File system paths
- Cloud storage settings

## Environment Variables

Use environment variables to override configuration values:

```bash
export MODEL_PATH=/path/to/models
export DATABASE_URL=postgresql://...
export REDIS_URL=redis://...
export LOG_LEVEL=INFO
```

## Validation

Configuration is validated on service startup with proper error handling.