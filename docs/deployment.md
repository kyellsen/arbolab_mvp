# Zero-Config Deployment Guide

This guide describes how to get ArboLab up and running locally with zero configuration.

## Quick Start
1. **Install Docker** (or Podman).
2. **Start the environment**:
   ```bash
   podman-compose up --build
   ```
3. **Access the App**: [http://localhost:8000](http://localhost:8000)

### Cleanup
```bash
podman-compose down -v
rm -rf ./data/input/* ./data/workspace/* ./data/results/*
```

---

## Directory Structure & Persistence
The system uses local bind mounts to ensure your data is accessible on the host and persists across restarts:

| Host Path | Container Path | Purpose |
| :--- | :--- | :--- |
| `./data/input` | `/data/input` | **Read-Only** raw input data. Drop your files here. |
| `./data/workspace` | `/data/workspace` | Working directory for heavy processing. |
| `./data/results` | `/data/results` | Final outputs and artifacts. |
| *Managed Volume* | `/var/lib/postgresql/data` | Database files (Postgres). |

## Advanced / Production Notes
- **SSL/HTTPS**: If you need SSL for local testing, use the archived script `./scripts/gen_certs.sh` and restore the Nginx configuration (see git history for `compose.yaml`).
- **Secrets**: For production, override the default environment variables in a `.env` file or your CI/CD pipeline:
    - `POSTGRES_USER`
    - `POSTGRES_PASSWORD`
    - `ARBO_DATABASE_URL`
- **Healthchecks**: The `app` service checks `http://localhost:8000/health`. It might take a few seconds after the database is ready.

## Troubleshooting
- **Logs**: `docker compose logs -f`
- **Shell Access**: `docker compose exec app /bin/bash`
- **Reset Database**: `docker compose down -v` (Warning: This deletes all DB data).
- **SELinux (Fedora/RHEL)**: If you get "Permission Denied" on mounts, ensure your volumes in `compose.yaml` have the `:Z` suffix (already included in the default config).

