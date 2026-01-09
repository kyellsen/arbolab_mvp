# Arbolab Codebase Audit Strategic Report (Revised)

This report summarizes the findings of a comprehensive audit performed on the Arbolab repository. The audit focused on architectural integrity, lab-level reproducibility, documentation accuracy, and frontend stability.

## 1. The "Recipe Gap" List
The following features bypass the "Recipe-First" architecture for Lab-specific state changes. Note: SaaS-level operations (User/Workspace management in PostgreSQL) are intentionally excluded from this list as they belong to the multi-tenant orchestration layer.

- **Lab Configuration Mutation:**
  - `apps/web/routers/settings.py`: Updates to Lab configuration (input/results paths, enabled plugins) currently write directly to `config.yaml` using `update_config`.
  - **Criticality**: High. These changes are NOT recorded as recipe steps (`modify_config`). Replaying a recipe on a new workspace would fail to re-enable required plugins or set the correct data paths.
- **Implicit Lab Initialization:**
  - `RecipeExecutor._record_step` implicitly adds an `open_lab` step if the recipe is empty.
  - **Criticality**: Medium. This captures the path but doesn't record the specific parameters or environment state at the time of opening.

## 2. Documentation Debt
Discrepancies identified between the `docs/` and the actual implementation:

- **`docs/architecture/runtime.md`**:
  - States `LabConfig` models are frozen (`pydantic.ConfigDict(frozen=True)`). 
  - **Reality**: They are currently mutable. Enforcing `frozen=True` is recommended for runtime stability and ensuring all changes are handled via reproducible commands.
- **Tailwind vs. Vanilla CSS Consistency**:
  - The project currently uses Tailwind CSS heavily. While Vanilla CSS is powerful for custom components, mixing styles without a clear boundary leads to documentation debt and maintenance complexity.
  - **Recommendation**: Maintain Tailwind for layout and utility-first styling; reserve Vanilla CSS for specialized scientific visualizations or complex animations where Tailwind becomes unmanageable.

## 3. Frontend & Stability Assessment
The following parts of the UI are identified as fragile or inconsistent:

- **The Explorer UI (`apps/web/templates/partials/explorer_content.html`)**:
  - **Hardcoded Logic**: The Alpine.js `resetInspector` function contains hardcoded HTML strings. These should be moved to a hidden Jinja2 partial or a template element.
  - **Dynamic Titles**: Logic like `activeEntity.split('_').map(...)` should be handled by the backend (e.g., via a helper or the ENTITY_MAP) to ensure UI/Backend naming consistency.
- **Unimplemented Details**:
  - `apps/web/main.py` contains hardcoded mock responses for tree/sensor details. These need to be connected to the actual DuckDB models through the `api.py` router.

## 4. Dead Code Inventory
Objects recommended for deletion or major cleanup:

- **Legacy Scripts**:
  - `scripts/migrate_v1_rbac.py` and `scripts/migrate_storage.py` (marked for archival).
- **Unused Core Modules**:
  - `packages/core/src/arbolab/core/recipes/transpiler.py`: Functional but disconnected.
- **MVP Hacks**:
  - `RecipeExecutor` (Line 57): "Implicitly record Lab.open".
  - `explorer.py` (Line 51): Unfinished logic for schema-based labels.

## 5. Refactoring Roadmap (Prioritized)

1.  **[High] Enforce Immutable Config**: Set `frozen=True` in `LabConfig` and implement a `modify_config` recipe step to record configuration changes.
2.  **[Medium] Explorer Component Refactor**: Move hardcoded Alpine HTML to partials and unify entity display names in the backend.
3.  **[Medium] Full Entity Integration**: Replace mock inspectors in `main.py` with dynamic routes using `apps.web.core.domain`.
4.  **[Medium] Recipe Export UI**: Connect the `RecipeTranspiler` to a "Download Recipe as Code" button in the dashboard.
5.  **[Low] Documentation Sync**: Update `runtime.md` and `recipes.md` to reflect the absolute separation between SaaS (Postgres) and Lab (DuckDB/Recipe) layers.
