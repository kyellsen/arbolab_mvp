# Services and Runtime Components

## Configuration Models and I/O
- Configuration is defined by immutable, versioned pydantic models such as `LabConfig` and `DataPaths`.
- `LabConfig`, `DataPaths`, and supporting dataclasses are declared as frozen (`pydantic.ConfigDict(frozen=True)` or `@dataclass(frozen=True)`) so runtime components cannot mutate injected settings.
- The root configuration provides defaults for all settings except the three storage roots, which must be specified directly or derived from a `base_root`.
- A dedicated config I/O module (for example `arbolab/services/config/io.py`) owns `load_config()` and `save_config()`, centralizes YAML access, and applies schema-version migrations.
- Validation uses strict, versioned pydantic schemas with migration paths per segment.
- The persisted YAML lives directly under `workspace_root` as `arbolab.yaml` and is the single source of truth for runtime configuration.
- There is no `ConfigManager`; configuration files are never read or written directly outside the config I/O module.
- `LabConfig` also carries plugin settings and numeric dtype controls (default float dtype and coercion toggle).

## Layouts, Stores, and Runtime Services
- `WorkspaceLayout` is the single authority for deriving and normalizing paths relative to `input_root`, `workspace_root`, and `results_root`, and enforces that derived internal paths cannot escape the configured roots. It is pure and performs no I/O.
- `ResultsLayout` builds on the workspace path rules to keep repeated structures (for example `results_root/plots/<project>/<experiment>/...`, timestamp suffixes, LaTeX folders) consistent and evolvable. It is pure and returns absolute `pathlib.Path` objects.
- `VariantStore` persists measurement stream datasets as Parquet variants and updates `DataVariant` metadata. It creates variant directories on demand and validates that stored paths never escape `workspace_root`.
- `ResultsWriter` prepares canonical directories for plots, LaTeX exports, CSV tables, and related publication artifacts by using `ResultsLayout`.
- `WorkspaceDatabase` owns DuckDB sessions rooted in the workspace database and exposes SQLAlchemy session factories or context managers.
- There is no standalone storage manager; I/O for creating directories lives with the stores and writers that need it.

Runtime components receive immutable configuration objects and do not mutate settings at runtime.

## Persistence Boundary
Persisted state includes configuration (with schema versions), project and domain data, and provenance. Layouts, stores, sessions, caches, and open connections are not persisted. Runtime changes require replacing the persisted YAML and restarting services.

## Service Integration
Infrastructure components with minimal domain logic live in dedicated packages (`arbolab-logger`, `arbolab-plot-service`, `arbolab-latex-service`). The core integrates with them through optional imports or injected factories and must not require them at import time. Plot/LaTeX services are optional extras and are not part of the MVP runtime.

`PlotService` implementations are hosted in `arbolab-plot-service` with pluggable backends (for example Matplotlib or Plotly). `LatexService` implementations live in `arbolab-latex-service` and produce `.tex` artifacts. Both services resolve output locations through `ResultsLayout` (and may use `ResultsWriter` for directory preparation) and write only to `results_root`.

Optional export services follow the same pattern and resolve output locations through `ResultsLayout`.

## Lab as Composition Root
`Lab` wires configuration, the logger from `arbolab-logger`, DuckDB, layouts, stores, and optional services, and exposes them through a small facade API (for example `lab.plot_service` and `lab.results_layout`). It is not a global singleton.

## Logging Expectations
- Constructing helpers, layouts, stores, and domain objects emits log entries at info or debug levels.
- Log levels are `debug`, `info`, `warning`, `error`, `critical`.
- Lazy initialization logs opened resources (file paths, plugin names) and elapsed time.
