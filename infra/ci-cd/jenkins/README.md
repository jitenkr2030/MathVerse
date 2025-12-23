# Jenkins Pipeline Configuration

This directory contains Jenkins pipeline definitions for MathVerse.

## Files

- **Jenkinsfile**: Declarative pipeline definition
- **scripts/**: Build and deployment scripts
- **groovy/**: Shared pipeline utilities

## Pipeline Stages

- **Checkout**: Source code retrieval
- **Test**: Automated testing
- **Build**: Docker image creation
- **Deploy**: Environment deployment
- **Notify**: Status notifications

## Usage

Configure Jenkins to use this pipeline definition.

## Plugins Required

- Pipeline: Groovy syntax support
- Docker: Docker integration
- Git: Source code management