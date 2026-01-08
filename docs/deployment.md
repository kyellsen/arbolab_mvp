# Deployment Guide

How to deploy ArboLab using Podman (or Docker).

## Prerequisites
- Podman and `podman-compose` (or Docker and Docker Compose).

## Directory Structure
The system uses the following volume mappings:
- `arbolab_data`: Persistent storage for project files (DuckDB, JSON, etc.) and raw input.
- `postgres_data`: Persistent storage for the SaaS database (Users, Org structure).

## Quick Start
1. **Build and Start**:
   ```bash
   podman-compose up --build -d
   ```
   
2. **Access the App**:
   Open [http://localhost:8000](http://localhost:8000).

3. **Login**:
   (Standard MVP login/register flow)

## Configuration
The application is configured via Environment Variables defined in `compose.yaml`.
- `ARBO_DATABASE_URL`: Connection string to Postgres.
- `ARBO_DATA_ROOT`: Directory inside the container where data resides (mapped to volume).

## Maintenance
- **Logs**: `podman-compose logs -f app`
- **Shell Access**: `podman-compose exec -it app /bin/bash`
