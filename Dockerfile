# Build Stage
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy generic workspace config
COPY pyproject.toml uv.lock ./

# Copy packages (simplified thanks to .dockerignore)
COPY packages ./packages

# Copy app (simplified)
COPY apps/web ./apps/web

# Install dependencies and build
# We rely on uv sync to create the venv.
ENV UV_COMPILE_BYTECODE=1
RUN uv sync --all-packages --no-dev


# Runtime Stage
FROM python:3.12-slim

# Install curl for healthcheck in runtime stage
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
# In this monorepo MVP setup, we copy the source code.
# In a strict production build, we might want to build wheels, but this is sufficient.
COPY packages ./packages
COPY apps/web ./apps/web

# Set ownership to appuser
RUN chown -R appuser:appuser /app

# Set path to use venv
ENV PATH="/app/.venv/bin:$PATH"
# Add src dirs to PYTHONPATH so editable installs work without full bind mounting
# We need to construct this path for all packages
ENV PYTHONPATH="/app/packages/arbolab/src:/app/packages/arbolab-logger/src:/app/packages/arbolab-linescale3/src:/app/packages/arbolab-treeqinetic/src:$PYTHONPATH"

# Defaults
ENV ARBO_DATA_ROOT="/data"
ENV ARBO_DATABASE_URL="postgresql://arbolab:arbolab@db:5432/arbolab"

# Switch to non-root user
USER appuser

# Expose
EXPOSE 8000

# Command
CMD ["uvicorn", "apps.web.main:app", "--host", "0.0.0.0", "--port", "8000"]
