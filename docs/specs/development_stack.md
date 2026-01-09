# Development Stack & Quality Gates

**Binding Rules**: See `../../AGENTS.md`.

## 1. Toolchain
- **Dependency Manager**: `uv`.
- **Linter/Formatter**: `ruff`.
- **Type Checker**: `mypy`.
- **Test Runner**: `pytest`.
- **Browser Tests**: `playwright` (via `pytest-playwright`).

## 2. Language Standards
- **Python**: `>= 3.12`.
- **Typing**: Explicit type hints **REQUIRED** for all functions/methods.
- **Docstrings**: Google Style **REQUIRED**.
- **Agent Output**: German (Chat), English (Code/Docs).

## 3. Library Contracts
- **Models**: `Pydantic v2` (Locked/Frozen by default).
- **Data Containers**: `dataclasses` (In-memory only).

## 4. Quality Gates (CI/Local)
Must pass before commit:
1. `uv run ruff check --fix packages/`
2. `uv run mypy packages/`
3. `uv run pytest`

## 5. Setup
`setup.sh` is the canonical bootstrap script. It MUST create `.venv` and sync dependencies via `uv`.

## 6. Browser Tests
Install Playwright browsers after dependency sync:
`uv run playwright install`
