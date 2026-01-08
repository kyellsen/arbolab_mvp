# AGENTS.md – Core Package (`arbolab`)

## Purpose
Defines responsibilities, boundaries, and constraints for the **core package** of the ArboLab platform. This package supplies the foundational domain model, configuration system, storage workflow, plugin runtime, and workspace management.

For repository-wide policies and documentation boundaries, see `AGENTS.md` and `docs/AGENTS.md`.

This file is the single source of truth for package-local scope and constraints within `packages/arbolab/`.

## Scope
The core package owns:
- The global **Lab** API and orchestration logic.

Not implemented yet:
- All configuration models (e.g., `LabConfig`, `DataPaths`) plus their persistence helpers.
- The domain model (Projects, Experiments, Treatments, etc.)
- The plugin registry and lifecycle under `arbolab.plugins`.
- Runtime components (`WorkspaceLayout`, `ResultsLayout`, `VariantStore`, `ResultsWriter`, `WorkspaceDatabase`).
- Integration points for the infrastructure packages `arbolab-logger`, `arbolab-plot-service`, and `arbolab-latex-service`.

Out of scope:
- Device- or sensor-specific parsers or metadata schemas beyond the shared abstractions.
- Any functionality that writes outside the managed storage roots.

## Responsibilities

### 1. Configuration & Storage Roots
Implements the storage-root and workspace lifecycle contracts defined in:
- `docs/specs/api.md`
- `docs/architecture/storage-format.md`

The core exposes immutable pydantic models (`LabConfig`, `DataPaths`) and YAML I/O helpers; `WorkspaceLayout` consumes these models and remains the authority for deriving and validating all workspace paths.

### 2. Domain Model
Maintains the SQLAlchemy declarative base, naming conventions, and every planned entity plus matching pydantic schemas.

### 3. Runtime Components (Layouts, Stores, Database)
The following components stay inside the core and are consumed by both services and plugins:

Not implemented yet:
- `WorkspaceLayout`
- `ResultsLayout`
- `VariantStore`
- `ResultsWriter`
- `WorkspaceDatabase`

### 4. External Infrastructure Packages
Actual implementations of logging and result services live outside the core:
- `arbolab-logger` → logger configuration and formatters used by `Lab` during bootstrap.

Not implemented yet:
- `arbolab-plot-service` → plotting backends that always resolve output targets through `ResultsLayout` (and may use `ResultsWriter`).
- `arbolab-latex-service` → LaTeX/export helpers that follow the same path guarantees.
The core only exposes the integration hooks and keeps the runtime components those packages rely on.

### 5. Plugin Runtime
Not implemented yet:
`arbolab.plugins` hosts the device registry, entry-point discovery, and lifecycle wiring. No device-specific logic is allowed in these modules. Plugin packages must place their parser and I/O layers in independent submodules (for example `arbolab_plugins.<device>.io.*`) so they can be reused without importing the core; only the plugin entry point touches `arbolab` to register capabilities.

### 6. Persistence & Path Rules
- Internal writes must remain under `workspace_root`.
- Plugins obtain write locations exclusively via `VariantStore` (workspace data) and `ResultsWriter` (publication artifacts).
- `results_root` is write-only for results-facing services (PlotService, LatexService, export helpers).
- `input_root` stays read-only across the stack.

## Testing Rules
- Tests live under `packages/arbolab/tests`.
- Every suite provisions temporary `input_root`, `workspace_root`, and `results_root` directories.
- Tests must not rely on `examples/` or hard-coded filesystem locations.

## Limitations / Forbidden Areas
- No device-specific logic in the core.
- No direct filesystem access outside stores and writers.
- No persistence of absolute paths or unmanaged directories.

## API Surface (planned)
- `Lab`
- `WorkspaceLayout`
- `ResultsLayout`
- `VariantStore`
- `ResultsWriter`
- `WorkspaceDatabase`
- Domain models and schemas
- Plugin registry

## Versioning & Migration
- Brand-new package: no migrations yet, but schema versioning is enforced through the configuration models.
