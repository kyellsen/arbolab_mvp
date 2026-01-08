# Architecture Context

**Binding Rules:** See `../../AGENTS.md`.

## Monorepo Structure

* **Core (`packages/arbolab`):** Shared domain models, runtime, `Lab` API.
* **Plugins (`packages/arbolab-<device>`):** Hardware-specific IO and mapping logic.
* **Infra:** Independent services (e.g., `arbolab-plot-service`).
* **Web App (`apps/`):** FastAPI app with SSR UI that orchestrates the `Lab` for SaaS use.

## Examples Layout

Each package under `packages/` owns a sibling subdirectory inside `examples/`.

```text
examples/
├── arbolab/            # Core examples
├── arbolab-logger/     # Infra examples
└── arbolab-<device>/   # Device specific examples
