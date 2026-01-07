# Technical Specifications

**Binding Rules**: See `../../AGENTS.md`.

These documents define the strict technical contracts for implementation.
Code must adhere to these schemas and interfaces explicitly.

## Specification Inventory

| File | Scope |
|:---|:---|
| **[`data-model.md`](./data-model.md)** | **Persistence & Schema:** DuckDB tables, SQL relations, types, and strict column definitions. |
| **[`api.md`](./api.md)** | **Runtime Interface:** `Lab` class API, workspace lifecycle, layouts, stores. |
| **[`metadata-package.md`](./metadata-package.md)** | **Exchange Format:** Frictionless Data Package structure (JSON/CSV) used for offline metadata and import. |
| **[`plugin-requirements.md`](./plugin-requirements.md)** | **Extension Protocol:** Rules for device plugins, entry points, and isolation boundaries. |
| **[`development_stack.md`](./development_stack.md)** | **Tooling:** Quality gates, linting (ruff), typing (mypy), and dependency management (uv). |
