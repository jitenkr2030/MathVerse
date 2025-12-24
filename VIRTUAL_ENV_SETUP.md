# MathVerse Python Virtual Environment Setup Guide

This document provides comprehensive instructions for setting up and managing Python virtual environments for all MathVerse services.

## Prerequisites

- Python 3.9 or higher (Python 3.12.5 is recommended)
- pip package manager
- Approximately 2GB of free disk space for dependencies

## Quick Start

### 1. Verify Python Installation

```bash
python3 --version
# Expected output: Python 3.12.x
```

### 2. Navigate to Project Root

```bash
cd /workspace/MathVerse
```

### 3. Activate a Service Environment

You can use the provided activation script to manage virtual environments:

```bash
# List all services and their status
python3 shared/activate_services.sh list

# Activate a specific service (e.g., backend)
python3 shared/activate_services.sh activate backend

# Install dependencies for a service
python3 shared/activate_services.sh install backend

# Update dependencies for a service
python3 shared/activate_services.sh update backend
```

Alternatively, you can manually activate environments:

```bash
# For backend
source apps/backend/venv/bin/activate

# For animation-engine
source services/animation-engine/venv/bin/activate

# For video-renderer
source services/video-renderer/venv/bin/activate

# For content-metadata
source services/content-metadata/venv/bin/activate

# For recommendation-engine
source services/recommendation-engine/venv/bin/activate
```

### 4. Install Dependencies

Once activated, install the required dependencies:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install service-specific dependencies
pip install -r requirements.txt

# Install shared base dependencies (optional)
pip install -r ../../shared/requirements_base.txt
```

## Service Virtual Environment Locations

| Service | Location | Port | Requirements File |
|---------|----------|------|-------------------|
| Backend API | `apps/backend/venv` | 8000 | `apps/backend/requirements.txt` |
| Animation Engine | `services/animation-engine/venv` | 8001 | `services/animation-engine/requirements.txt` |
| Video Renderer | `services/video-renderer/venv` | 8002 | `services/video-renderer/requirements.txt` |
| Content Metadata | `services/content-metadata/venv` | 8003 | `services/content-metadata/requirements.txt` |
| Recommendation Engine | `services/recommendation-engine/venv` | 8004 | `services/recommendation-engine/requirements.txt` |

## Environment Configuration

### 1. Copy Environment Template

Each service includes an `.env.example` file. Copy it to `.env` and customize:

```bash
# Example for backend
cp apps/backend/.env.example apps/backend/.env

# Example for animation-engine
cp services/animation-engine/.env.example services/animation-engine/.env
```

### 2. Required Environment Variables

All services require the following basic configuration:

```env
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=<service-specific-port>
DEBUG=true
LOG_LEVEL=debug
DATABASE_URL=postgresql+asyncpg://mathverse:mathverse@localhost:5432/<database-name>
REDIS_URL=redis://localhost:6379/<redis-db>
```

## Managing Dependencies

### Adding New Dependencies

1. Activate the target service environment
2. Install the package:
   ```bash
   pip install package-name
   ```
3. Save the exact version to requirements.txt:
   ```bash
   pip freeze > requirements.txt
   ```

### Updating Dependencies

```bash
# Activate the environment first
source services/<service>/venv/bin/activate

# Update all dependencies
pip install --upgrade -r requirements.txt
```

### Checking Installed Packages

```bash
pip list
pip show package-name
```

## Development Workflow

### Running a Service

```bash
# Activate the environment
source services/<service>/venv/bin/activate

# Start the service (example for backend)
cd apps/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Activate the environment
source services/<service>/venv/bin/activate

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Code Formatting and Linting

```bash
# Format code
black .

# Sort imports
isort .

# Run linter
pylint app/

# Type checking
mypy app/
```

## Troubleshooting

### Virtual Environment Not Found

If you receive an error about the virtual environment not existing:

```bash
# Create the virtual environment
python3 -m venv services/<service>/venv

# Install dependencies
source services/<service>/venv/bin/activate
pip install -r services/<service>/requirements.txt
```

### Package Installation Fails

If pip installation fails with permission errors:

```bash
# Use --user flag
pip install --user -r requirements.txt

# Or ensure virtual environment is activated
source services/<service>/venv/bin/activate
pip install -r requirements.txt
```

### Import Errors

If imports fail after installing packages:

```bash
# Verify the package is installed
pip list | grep package-name

# Reinstall the package
pip uninstall package-name
pip install package-name

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Database Connection Issues

Ensure PostgreSQL and Redis are running:

```bash
# Check PostgreSQL
pg_isready -h localhost -p 5432

# Check Redis
redis-cli ping
```

## Best Practices

1. **Always activate the virtual environment** before working on a specific service
2. **Use the requirements.txt files** to ensure reproducible environments
3. **Keep dependencies updated** but test thoroughly before committing changes
4. **Use the .env.example files** as templates, never commit actual .env files
5. **Run tests locally** before pushing changes to ensure compatibility
6. **Document any new dependencies** added to requirements files

## Additional Resources

- [Python Virtual Environments Documentation](https://docs.python.org/3/tutorial/venv.html)
- [pip User Guide](https://pip.pypa.io/en/stable/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
