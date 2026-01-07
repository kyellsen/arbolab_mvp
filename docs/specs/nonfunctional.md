# Nonfunctional and Process Requirements

## Language and Code Standards
- Repository content (code, docs, comments, commits, configs) must be English.
- Chat output produced by agents MUST be German.
  (Human-facing explanations only; never committed files.)
- Python version is >= 3.12.
- Every module, class, function, and method must provide explicit type hints and a Google-style docstring describing purpose, key parameters, and return values (where applicable).
- Pydantic models are the standard for persisted time-series metadata and configuration data; in-memory dataset containers may use dataclasses.

## Tooling and Environment
- Each package defines metadata and dependencies in its own `pyproject.toml`.
- Dependency and environment management uses `uv`.
  - Create and activate a local virtual environment with `uv venv`.
  - Install dependencies with `uv sync`.
- Linting and formatting use `ruff`.

## Linting, Typing, and Tests
Run these before every commit:
- `uv run ruff check --fix packages/`
- `uv run mypy packages/`
- `uv run pytest`

The root `pyproject.toml` configures `uv` workspace members and ensures `ruff`, `mypy`, and `pytest` see all package `src/` trees (via `mypy_path`, `files`, and pytest `addopts`).

## Setup Script
`setup.sh` initializes a development environment by:
- Verifying that `uv` is installed.
- Creating or recreating `.venv`.
- Running `uv sync` to install workspace packages and dev dependencies.
- Printing commands for running tests, `ruff`, and `mypy`.

## Agent Documentation
Package-specific `AGENTS.md` files (for example under `packages/`) are governed
by the root `AGENTS.md`.
