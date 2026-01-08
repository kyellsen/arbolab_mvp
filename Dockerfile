# Build Stage
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy generic workspace config
COPY pyproject.toml uv.lock ./

# Copy packages
COPY packages/core ./packages/core
COPY packages/arbolab-logger ./packages/arbolab-logger

# Copy app
COPY apps/web ./apps/web

# Install dependencies and build
# We rely on uv sync to create the venv.
# Because we are in a container, we can install into system or a specific venv.
# Using /app/.venv is fine.
ENV UV_COMPILE_BYTECODE=1
RUN uv sync --locked --no-dev --frozen

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*


# Runtime Stage
FROM python:3.12-slim

WORKDIR /app

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code (needed for runtime if not installed as editable, 
# but uv sync defaults to editable for workspace members, so we must copy source too)
# Actually, for production, better to build wheels. 
# But for this MVP/Monorepo setup, copying source + venv is easiest.
COPY packages/core/src /app/packages/core/src
COPY packages/arbolab-logger/src /app/packages/arbolab-logger/src
COPY apps/web /app/apps/web

# Set path to use venv
ENV PATH="/app/.venv/bin:$PATH"
# Add src dirs to PYTHONPATH so editable installs work without full bind mounting
ENV PYTHONPATH="/app/packages/core/src:/app/packages/arbolab-logger/src:$PYTHONPATH"

# Defaults
ENV ARBO_DATA_ROOT="/data"
ENV ARBO_DATABASE_URL="postgresql://arbolab:arbolab@db:5432/arbolab"

# Expose
EXPOSE 8000

# Command
CMD ["uvicorn", "apps.web.main:app", "--host", "0.0.0.0", "--port", "8000"]
