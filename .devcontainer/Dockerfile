FROM python:3.12-slim

# 1. System-Tools & Playwright Dependencies pre-install
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- FIX FÜR GIT AUF LINUX/PODMAN ---
# Erlaubt git den Zugriff auf /app, auch wenn die Datei-Owner (Host 1000 vs Container 0) nicht matchen.
RUN git config --system --add safe.directory /app

# 2. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Environment Variables
ENV UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/packages/arbolab/src:/app/packages/arbolab-logger/src:/app/packages/arbolab-linescale3/src:/app/packages/arbolab-treeqinetic/src:$PYTHONPATH"

WORKDIR /app
