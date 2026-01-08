# Zero-Config Deployment Guide

This guide describes how to get ArboLab up and running locally with zero configuration.

## Quick Start
1. **Install Docker** (or Podman).
2. **Start the environment**:
   ```bash
   podman-compose up --build
   ```
3. **Access the App**: [http://localhost:8000](http://localhost:8000)

### Factory Reset (Deep Clean)
To completely reset the environment (e.g., to clear a corrupted database or start fresh), follow these steps.

**Option A: Operational Reset (Keeps Input Data)**
*Note: Since data is nested by User/Workspace, manual granular cleanup is difficult. This command clears known nested workspace/result folders but leaves input/ alone.*
```bash
# 1. Stop containers
podman-compose down -v

# 2. Clear generated data (preserves input folders)
# Finds and deletes 'workspace' and 'results' directories at any depth
find ./data -name "workspace" -type d -exec rm -rf {} +
find ./data -name "results" -type d -exec rm -rf {} +
# Also clear the main saas.db if it exists in data root (rare)
rm -f ./data/saas.db

# 3. Restart
podman-compose up --build
```

**Option B: Total Wipe (Nuclear Option)**
**WARNING**: This deletes EVERYTHING in `./data`, including all inputs and user directories.
```bash
podman-compose down -v
# Clean everything in data/
rm -rf ./data/*
# Restart
podman-compose up --build
```

---

## Directory Structure & Persistence
The system uses local bind mounts to ensure your data is accessible on the host and persists across restarts:

| Host Path | Container Path | Purpose |
| :--- | :--- | :--- |
| `./data` | `/data` | **Root Data Volume**. Persists all user workspaces and inputs. |
| `↳ ./data/<uid>/<wid>/input` | `.../input` | Isolated input per workspace. |
| `↳ ./data/<uid>/<wid>/workspace` | `.../workspace` | Isolated scratch space. |
| `↳ ./data/<uid>/<wid>/results` | `.../results` | Isolated results. |
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

