# GitLab CI Configuration

This directory contains GitLab CI/CD pipeline configurations for MathVerse.

## Files

- **.gitlab-ci.yml**: Main pipeline configuration
- **deploy/**: Deployment scripts
- **test/**: Test configurations

## Stages

- **test**: Run automated tests
- **build**: Build Docker images
- **deploy**: Deploy to environments
- **security**: Security scanning

## Usage

Pipeline runs automatically on commits and merges.

## Variables

Configure CI/CD variables in GitLab project settings.