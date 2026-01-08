# ArboLab API (Lab) Specification

**Binding Rules**: See `../../AGENTS.md`.

## 1. The Lab Interface
The `Lab` class is the single public entry point.

### Responsibilities
- **Lifecycle**: Open/Create workspaces.
- **Wiring**: Initialize `WorkspaceDatabase`, `VariantStore`, `ResultsLayout`, `PluginRuntime`.
- **Safety**: Enforce read-only input roots.

### Workspace Lifecycle Contract
`Lab.open(...)` MUST:
1. Support explicit roots (`input_root`, `workspace_root`, `results_root`) OR `base_root` derivation.
2. Load `workspace_root/config.yaml` if exists.
3. Create `workspace_root/config.yaml` if missing (bootstrap).
4. **Idempotency**: Opening an existing workspace returns the configured instance without side effects.

## 2. Directory & Path Contracts

### 2.1 Storage Layout
| Root | Permission | Content |
|:---|:---|:---|
| `input_root` | **READ-ONLY** | User data, raw CSVs, `metadata/datapackage.json`. |
| `workspace_root` | **READ/WRITE** | `arbolab.duckdb`, `config.yaml`, internal Parquet, logs. |
| `results_root` | **WRITE-ONLY** | Publication artifacts (Plots, Reports). **Never** pipeline input. |

### 2.2 Path Safety
- All paths MUST be absolute `pathlib.Path` objects.
- Callers MUST use `WorkspaceLayout` / `ResultsLayout` helpers (e.g., `workspace_subdir()`).
- String concatenation for paths is **FORBIDDEN**.

## 3. Configuration Hierarchy

Configuration resolution order (Highest to Lowest priority):
1. **Runtime Arguments**: Passed to `Lab.open()`.
2. **Environment Variables**: e.g., `ARBOLAB_DB_PATH`.
3. **Workspace Config**: `workspace_root/config.yaml` (TOML/YAML).
4. **Defaults**: Hardcoded library defaults.

### Plugin Component Configuration
- `config.yaml` MUST contain an allow-list of enabled plugins.
- Empty list = No plugins loaded.
- Plugins receive a namespaced config section.

## 4. Services & persistence
- **Database**: Access via `lab.database.session()`. Ad-hoc engine creation is FORBIDDEN.
- **Metadata**: Import/Validation via `lab.metadata.import_package()`.
- **Analytics**: Large datasets return **Arrow/Parquet** objects, not JSON.

## 5. Recipe Contract
Recipes provide a declarative execution plan for the Web App.

### 5.1 Requirements
- The Web App MUST require a Recipe for any ingest or analysis execution.
- Direct Python usage of the `Lab` MUST remain recipe-optional.
- The canonical Recipe path is `workspace_root/recipes/recipe.json`.
- Recipe JSON MUST include:
  - `recipe_version` (semantic version string)
  - `steps` (ordered list)
- Each `steps[]` entry MUST include:
  - `type` (string step identifier)
  - `params` (object)
- Step parameters that reference input files MUST use paths relative to `input_root`.
  Absolute paths are FORBIDDEN.

### 5.2 Execution
- The core MUST provide `Lab.run_recipe(...)` that maps step types to Lab operations.
- Recipe execution MUST be idempotent; re-running a Recipe must not duplicate persisted state.
- The Web App MAY expose a "view as Python" export derived from the Recipe; direct Python usage does not require this export.

## 6. Web App API (SaaS)
The Web App is an optional SaaS layer that orchestrates the `Lab` through HTTP.

### 6.1 Authentication (MVP)
- `POST /auth/login` accepts a name and password and establishes a session.
- The MVP uses a single test user; no registration or password reset is required.
- Authentication data is stored in the SaaS metadata store (separate from Workspace DuckDB).

### 6.2 Workspaces
- `POST /workspaces` creates a Workspace from explicit roots or a `base_root`.
- `GET /workspaces` lists registered Workspaces.
- The Web App MUST use the same root safety rules as `Lab.open(...)`.

### 6.3 Recipes
- `PUT /workspaces/{id}/recipe` persists the Recipe to the canonical Recipe path.
- `POST /workspaces/{id}/recipe/run` executes the stored Recipe.
- Execution responses MAY return HTML fragments for HTMX updates.

### 6.4 Components (Optional)
- `GET /components/plot/{id}` returns a server-rendered Plotly HTML fragment.
- `GET /components/log-viewer` returns log output suitable for polling.
