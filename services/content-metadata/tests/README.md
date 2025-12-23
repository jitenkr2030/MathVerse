# Content Metadata Service Tests

This directory contains test suites for the content metadata service.

## Test Types

- **unit/**: Unit tests
- **integration/**: Integration tests
- **e2e/**: End-to-end tests
- **performance/**: Performance tests

## Running Tests

```bash
# Run all tests
pytest

# Run specific test type
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## Test Data

Use fixtures and mock data for consistent testing.

## CI/CD

Tests run automatically in CI/CD pipelines.