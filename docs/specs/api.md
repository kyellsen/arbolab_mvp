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
2. Load `workspace_root/arbolab.yaml` if exists.
3. Create `workspace_root/arbolab.yaml` if missing (bootstrap).
4. **Idempotency**: Opening an existing workspace returns the configured instance without side effects.

## 2. Directory & Path Contracts

### 2.1 Storage Layout
| Root | Permission | Content |
|:---|:---|:---|
| `input_root` | **READ-ONLY** | User data, raw CSVs, `metadata/datapackage.json`. |
| `workspace_root` | **READ/WRITE** | `arbolab.duckdb`, `arbolab.yaml`, internal Parquet, logs. |
| `results_root` | **WRITE-ONLY** | Publication artifacts (Plots, Reports). **Never** pipeline input. |

### 2.2 Path Safety
- All paths MUST be absolute `pathlib.Path` objects.
- Callers MUST use `WorkspaceLayout` / `ResultsLayout` helpers (e.g., `workspace_subdir()`).
- String concatenation for paths is **FORBIDDEN**.

## 3. Configuration Hierarchy

Configuration resolution order (Highest to Lowest priority):
1. **Runtime Arguments**: Passed to `Lab.open()`.
2. **Environment Variables**: e.g., `ARBOLAB_DB_PATH`.
3. **Workspace Config**: `workspace_root/arbolab.yaml` (TOML/YAML).
4. **Defaults**: Hardcoded library defaults.

### Plugin Component Configuration
- `arbolab.yaml` MUST contain an allow-list of enabled plugins.
- Empty list = No plugins loaded.
- Plugins receive a namespaced config section.

## 4. Services & persistence
- **Database**: Access via `lab.database.session()`. Ad-hoc engine creation is FORBIDDEN.
- **Metadata**: Import/Validation via `lab.metadata.import_package()`.
- **Analytics**: Large datasets return **Arrow/Parquet** objects, not JSON.
