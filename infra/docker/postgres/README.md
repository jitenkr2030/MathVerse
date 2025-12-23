# PostgreSQL Configuration

This directory contains PostgreSQL database configuration for MathVerse.

## Files

- **init.sql**: Database initialization script
- **postgresql.conf**: PostgreSQL configuration
- **pg_hba.conf**: Authentication configuration

## Environment Variables

- **POSTGRES_DB**: Database name
- **POSTGRES_USER**: Database user
- **POSTGRES_PASSWORD**: Database password

## Usage

Configuration is used in Docker containers and Kubernetes deployments.

## Backups

Configure regular backups using pg_dump or WAL archiving.