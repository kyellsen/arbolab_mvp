# Runtime & Services

## Configuration (`LabConfig`)
* **Immutability:** Models are frozen (`pydantic.ConfigDict(frozen=True)`). No runtime mutation.
* **Source:** Single `arbolab.yaml` in `workspace_root`.
* **Migration:** Versioned schemas handled by `arbolab/services/config/io.py`.
* **Scope:** Defines plugins, default numeric dtypes, and plugin settings.

## Lab Composition Root
The `Lab` class is the integration point, not a global singleton. It wires:
1.  **Config:** Loads `LabConfig`.
2.  **Layouts:** Injects `WorkspaceLayout` & `ResultsLayout`.
3.  **Stores:** Wires `VariantStore` & `WorkspaceDatabase`.
4.  **Services:** Connects `PlotService` / `LatexService` (if available).

## Web App (SaaS)
The Web App is an optional SaaS layer that orchestrates the `Lab`:
* **Framework:** FastAPI with server-side rendering (Jinja2) and HTMX for partial updates.
* **UI:** Tailwind CSS for styling; Plotly for server-rendered charts.
* **Capabilities:** Create and configure Workspaces, persist Recipes, execute Recipes, and display results.
* **Separation:** Direct Python usage of the `Lab` remains recipe-optional and unaffected.

## SaaS Metadata Store
The Web App maintains a small metadata store for SaaS concerns:
* **Contents:** Users, Tenants, sessions, and Workspace registrations.
* **MVP Backend:** SQLite, accessed via SQLAlchemy.
* **Upgrade Path:** Must be swappable to PostgreSQL without changing core domain storage.
* **MVP Scope:** Single test user and single-tenant operation.

## Service Boundaries
* **Core:** Pure Python, standard library + minimal deps (NumPy/Pandas/Polars).
* **Infra Packages:** `arbolab-plot-service`, `arbolab-latex-service`.
    * Core integrates via optional imports/factories.
    * Core **must not** hard-depend on them.
* **Persistence:** Layouts and Stores are stateless helpers; state lives in the FS/DB.

## Logging
* Levels: `debug`, `info`, `warning`, `error`, `critical`.
* Lazy initialization logs opened resources.
