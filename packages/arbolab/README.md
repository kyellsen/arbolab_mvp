# Arbolab Core (`arbolab`)

Core workspace package for the Arbolab platform. It provides the central domain models, configuration systems, and runtime orchestration.

## Scope

- Central `Lab` API and orchestration.
- Configuration models (`LabConfig`) and persistence.
- Domain models (Projects, Experiments, Results, etc.) via SQLAlchemy.
- Data persistence management (DuckDB for metadata, Parquet for observations).
- Plugin registry and lifecycle management.
- Runtime components (`WorkspaceLayout`, `ResultsLayout`, `VariantStore`).

## API Surface

- `arbolab.Lab`: Main entry point for workspace operations.
- `arbolab.config.LabConfig`: Configuration management.
- `arbolab.layout.WorkspaceLayout` / `ResultsLayout`: Path orchestration.
- `arbolab.database.WorkspaceDatabase`: Metadata and domain entity access.
- `arbolab.store.VariantStore`: Data variant (Parquet) persistence.
- `arbolab.models.core`: Domain entities.

## Guiding Principles

- **Read-Only Ingest**: `input_root` is strictly read-only.
- **Write-Managed**: All writes must go through managed layouts under `workspace_root` or `results_root`.
- **Analytics-First**: Optimized for DuckDB/Parquet workflows.
- **Isolation**: No device-specific logic in the core.

## Development

Tests are located in `tests/` and can be run via `pytest`.

## Examples

Examples are located in the top-level [`examples/arbolab`](../../examples/arbolab) directory.
