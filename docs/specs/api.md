# ArboLab API (Lab)

## Purpose and Scope
This document defines ArboLab's single public API surface: the `Lab`.
Notebooks, scripts, and CLI tools interact with ArboLab by opening/creating a
Lab workspace and then using the entities, layouts, stores, and services
exposed by that Lab instance.

Former separate "core" and "domain" API specifications are consolidated into
this document.

## Principles
- Single entry point: callers interact only through the `Lab` API.
- Domain-first: APIs speak the ubiquitous language (see `docs/requirements/glossary.md`).
- Analytics-first: full-resolution observations remain Parquet/DuckDB-first; the
  API returns large datasets as Arrow/Parquet, not as JSON payloads.
- Safety: `input_root` is read-only; writes go only to `workspace_root` and
  `results_root`.
- Stable joins: IDs are stable within a workspace and are the primary join keys
  across metadata and analytics outputs.

## Lab Responsibilities (Surface Area)
The `Lab` is responsible for preparing and wiring:
- storage roots and workspace layout
- configuration loading/saving (including schema migrations)
- logging and diagnostics
- DuckDB and the workspace database runtime (`WorkspaceDatabase`)
- workspace and results layouts
- variant store and results writer
- plugin discovery/registration and plugin lifecycle hooks

The `Lab` exposes a single cohesive surface that includes:
- workspace lifecycle (open/create)
- configuration access
- database/session access
- layout and storage access (via layouts, stores, and writers)
- domain and metadata operations (import, validation, navigation)
- analytics execution and dataset materialization (as part of the same Lab surface)

## Workspace Lifecycle Contract

### Opening and Creating Workspaces
- `Lab.open(...)` must support opening a workspace from either:
  - `base_root` (derive default roots), or
  - explicit `input_root`, `workspace_root`, and `results_root`, or
  - `config_path` pointing to an existing workspace config.
- A workspace must have a persisted configuration document at `workspace_root/arbolab.yaml`.
- When `arbolab.yaml` exists, `Lab.open(...)` must load it and open the workspace.
- When `arbolab.yaml` does not exist, `Lab.open(...)` must create it from the provided roots and persist it.

### Storage Roots and Safety
- `input_root` is treated as read-only input data.
  - When explicit roots are provided, `input_root` must exist and must be a directory.
  - When `base_root` is used, ArboLab may create the derived `input_root` directory if it does not exist, but must still treat it as read-only input afterwards.
- `workspace_root` stores internal state (database, Parquet variants, logs, caches, intermediate artifacts).
- `results_root` stores publication-ready outputs (plots, exports, reports) and is never treated as pipeline input.

### Idempotency Expectations
- Opening the same workspace repeatedly must be safe and must not create duplicate configuration state.
- Workspace initialization must not modify experiment input directories under `input_root` beyond reading their contents.

## Configuration Access
- Configuration is loaded and saved exclusively via the config I/O module.
- Schema migrations are applied on load before returning any models.
- Runtime config changes require updating the persisted YAML and restarting services.
- The configuration file must live directly inside `workspace_root` as `arbolab.yaml`.
- The configuration must include an allow list of enabled plugin entry point names (for example `enabled_plugins`); an empty list disables plugin discovery.

## Database and Sessions
- The workspace database must be located under `workspace_root` and must be managed through the Lab-provided database runtime.
- Callers must obtain SQLAlchemy sessions through the Lab API (for example `lab.database.session()`) rather than constructing engines or connections ad-hoc.
- Schema creation must be driven by registered SQLAlchemy `MetaData` collections and must include plugin metadata contributions.

## Path and Storage Access
- All path derivations go through `WorkspaceLayout` and `ResultsLayout`; callers must not construct ad-hoc path strings.
- `WorkspaceLayout` exposes helpers such as `workspace_subdir()` and `results_subdir()`.
- Layouts return absolute `pathlib.Path` objects to avoid subtle bugs from string concatenation or platform-specific separators.
- Directory creation is handled by `VariantStore` and `ResultsWriter` on demand; there is no standalone storage manager.

## Domain and Metadata Operations
The Lab-owned domain and metadata operations are responsible for:
- importing metadata packages into the workspace database (see `docs/specs/metadata-import.md`)
- validating references and producing human-readable validation reports
- exposing queryable views of Projects, Experiments, Runs, and their execution context (TreatmentApplications and SensorDeployments)
- managing assets and measurement metadata required to link raw files, streams, and observation datasets

### Data Access Shape (Guidance)
Domain/metadata operations should return small, JSON-friendly objects:
- entity records (IDs, names, properties, lifecycle timestamps)
- lists of IDs and lightweight summaries
- explicit links between domain entities (for example Run → Experiment, Run → overlapping TreatmentApplications, Run → active SensorDeployments)

Large datasets (time-series and derived tables) must be returned as Arrow
or Parquet.

### Stability Rules
- IDs are stable within a workspace and are the primary join keys across domain metadata and analytics outputs.
- Optional human IDs may exist (for example in `domain_ids`) but must not be used as join keys in persisted analytics outputs.
- API contracts must be versioned and remain backwards compatible within a major version line.

## Data Access and Results
- Raw input data is read only from `input_root`.
- Internal files and metadata are produced under `workspace_root`.
- Publication artifacts are written under `results_root` and are never treated as pipeline inputs.
- Variant persistence and ingestion rules are specified in `docs/specs/data-variants.md`.
- Results/output rules are specified in `docs/specs/results-outputs.md`.

## Plugin Runtime
- Plugins are discovered and registered through the Lab-managed plugin runtime.
- The runtime must load only the explicitly enabled entry points and must not import disabled plugins.
- When enabled plugins are missing, the Lab must emit actionable diagnostics.
- Plugin discovery, registration, and schema contributions are specified in `docs/specs/plugin-requirements.md`.

## References
- `docs/requirements/glossary.md`
- `docs/specs/data-model.md`
- `docs/specs/metadata-import.md`
- `docs/specs/data-variants.md`
- `docs/specs/results-outputs.md`
- `docs/specs/plugin-requirements.md`
- `docs/specs/nonfunctional.md`
