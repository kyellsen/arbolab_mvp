# Arbolab Structural Audit Report

## 1. Architectural Violations

> [!IMPORTANT]
> **SaaS Logic in Core**
> `packages/core/src/arbolab/config.py` contains a `database_url` field with a default PostgreSQL connection string. 
> Core should remain a standalone library for local/notebook use (DuckDB-native) and should NOT have knowledge of the SaaS PostgreSQL database. This should be moved to `apps/web`.

*   **Dependency Leakage:** No direct imports from `apps/web` into `packages/core` were found, which is good. However, the configuration model in Core is "pre-polluted" with SaaS-specific fields.

## 2. Configuration Mismatches

*   **Mypy Path Mismatch:** In the root `pyproject.toml`, `tool.mypy.mypy_path` references `packages/arbolab/src`, but the actual directory is `packages/core/src`. This breaks type checking for the core package.
*   **Docker/Compose Redundancy:** 
    *   The `Dockerfile` explicitly copies `src` directories for all packages, while `compose.yaml` bind-mounts the entire `packages/` directory. 
    *   The `ARBO_DATABASE_URL` is hardcoded in the `Dockerfile` as a fallback, which contradicts the 12-factor approach used in `.env.example`.
*   **Python Version Sync:** All `pyproject.toml` files agree on `python >= 3.12`.

## 3. Hygiene Report

*   **`plugins/` (Root):** This directory is empty and currently unused. Logic seems to have moved to `packages/arbolab-*`.
*   **`scripts/temp/`:** Contains temporary/junk files that should be ignored or deleted.
*   **Folder Naming:** The inconsistency between `packages/core` (folder name) and `arbolab` (package name) is managed via `hatch`, but creates cognitive load. Recommendation: Rename `packages/core` to `packages/arbolab`.
*   **Data Persistence:** `ARBO_DATA_ROOT` is consistently used, but internal folder structures (`input/`, `workspace/`) are defined in Core's `LabConfig`.

## 4. Restructuring Plan

### Phase 1: Clean Root & Configs
1.  **Delete** empty `/plugins` directory in root.
2.  **Move** `packages/core` to `packages/arbolab` for naming consistency.
3.  **Update** root `pyproject.toml` `mypy_path` to point to the correct source routes.
4.  **Refactor** `Dockerfile` to use a more dynamic discovery of workspace packages during copy.

### Phase 2: Decouple Core from SaaS
1.  **Remove** `database_url` and all PostgreSQL-specific logic from `packages/core/src/arbolab/config.py`.
2.  **Extend** `LabConfig` in `apps/web` (SaaS layer) to include PostgreSQL and Auth settings.

### Phase 3: Infrastructure Alignment
1.  **Standardize** `.env` handling across Local Dev and Docker.
2.  **Clean up** `scripts/` by moving verification scripts into their respective package `tests/` or a dedicated `qa/` folder.
