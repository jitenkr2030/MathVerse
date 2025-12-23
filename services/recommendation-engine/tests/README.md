# Recommendation Engine Tests

This directory contains test suites for the recommendation engine service.

## Test Types

- **unit/**: Unit tests for individual components
- **integration/**: Integration tests for service interactions
- **ml-tests/**: Machine learning model tests
- **performance/**: Performance and load tests
- **data-validation/**: Data quality tests

## Running Tests

```bash
# Run all tests
pytest

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/ml-tests/

# Run with coverage
pytest --cov=src tests/

# Run model tests
pytest tests/ml-tests/ -v
```

## Test Data

- **fixtures/**: Test data fixtures
- **mock-data/**: Mock datasets for testing
- **expected-outputs/**: Expected test results

## Model Validation

Test model accuracy and performance:
- Precision/Recall metrics
- Recommendation quality
- Performance benchmarks
- Data validation checks

## CI/CD

Tests run automatically in CI/CD pipelines with model validation checks.