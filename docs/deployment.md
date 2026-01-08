# Deployment Guide
> [!IMPORTANT]
> **Production Notice**: This guide describes a "semi-production" setup using Nginx, separated volumes, and externalized secrets. It is much more robust than the dev setup but still requires care (e.g., backing up volumes, rotating secrets).

## Prerequisites
- Podman and `podman-compose` (or Docker and Docker Compose).

## Directory Structure & Volumes
The system now uses specific volume mappings for better data management:

| Volume Name | Container Path | Purpose | Recommended Type |
| :--- | :--- | :--- | :--- |
| `postgres_data` | `/var/lib/postgresql/data` | Database files (Users, Org structure) | Named Volume / Managed Storage |
| `arbolab_input` | `/data/input` | **Read-Only** raw input data | Bind Mount (to large storage) or Volume |
| `arbolab_workspace` | `/data/workspace` | Working directory for heavy processing | Named Volume (Fast I/O) |
| `arbolab_results` | `/data/results` | Final outputs and artifacts | Bind Mount / Volume |

## Configuration
Configuration is managed via the `.env` file. **Do not commit `.env` to Git.**

1. **Create Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env and set strong passwords!
   ```

2. **Generate TLS Certificates** (for local SSL):
   ```bash
   ./scripts/gen_certs.sh
   ```
   This creates self-signed certs in `./certs/` which are mounted into Nginx.

## Start & Run
1. **Build and Start**:
   ```bash
   podman-compose up --build -d
   ```
   
2. **Healthchecks**:
   The containers have configured healthchecks.
   - **DB**: Checks `pg_isready`.
   - **App**: Checks `curl localhost:8000/health`.
   - **Nginx**: Depends on App being healthy.

3. **Access**:
   - **HTTP**: [http://localhost](http://localhost) (Port 80)
   - **HTTPS**: [https://localhost](https://localhost) (Port 443) - *Accept the self-signed warning.*

## Maintenance
- **Logs**: `podman-compose logs -f`
- **Shell**: `podman-compose exec -it app /bin/bash`
- **Updates**:
    ```bash
    git pull
    podman-compose up --build -d
    ```

## Security Checklist (Production)
- [ ] Change all default passwords in `.env`.
- [ ] Replace self-signed certs in `./certs` with valid CA-signed certs.
- [ ] Ensure `arbolab_input` is strictly Read-Only at the filesystem level if possible.
- [ ] Firewall: Block port 8000 (App) and 5432 (DB) from external access; only allow 80/443 (Nginx).
