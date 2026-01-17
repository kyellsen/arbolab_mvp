FROM python:3.12-slim

# 1. System-Tools & Playwright Dependencies pre-install
# We install base tools here. Playwright --with-deps does the rest later.
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Install uv (directly from official installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Environment Variables for Python & uv
ENV UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Add all package sources to PYTHONPATH so imports work
    PYTHONPATH="/app/packages/arbolab/src:/app/packages/arbolab-logger/src:/app/packages/arbolab-linescale3/src:/app/packages/arbolab-treeqinetic/src:$PYTHONPATH"

WORKDIR /app
