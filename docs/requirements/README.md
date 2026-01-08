# Requirements & Vision

**Binding Rules:** See `../../AGENTS.md`.

## Implementation Status (MVP)

| ID | Title | Status |
|----|-------|--------|
| US-001 | Create or open a Lab | **Partial** (Core Lab implemented) |
| US-002 | Offline experiment documentation package | Planned |
| US-004 | Import metadata package into Lab DB | **Done** (via `MetadataImporter`) |
| US-005 | Discover and load plugins | Planned |
| US-006 | Link metadata to raw sensor files | Planned |
| US-007 | Ingest raw sensor data into variants | Planned |
| US-008 | Web Login MVP | Planned |
| US-009 | Run Recipe via Web | Planned |

## Vision
ArboLab makes full-resolution experimental sensor data analysis reproducible and ergonomic.
* **Analytics-first:** DuckDB-backed analysis on full-resolution Parquet observations.
* **Domain-first:** Models experiments in scientific terms (Treatments, Runs), not just "files".
* **Reproducible:** Raw inputs are read-only; intermediate datasets are persisted versions.

## Scope & Personas

### 1. Researcher (Primary MVP)
* **Goal:** Explore and analyze tree sensor data with maximal flexibility.
* **Interaction:** Jupyter notebooks, custom pipelines.
* **Needs:** Composable APIs, inspectable intermediates, validatable metadata.

### 2. SaaS User (MVP Minimal)
* **Goal:** Create and configure Workspaces and run Recipes through a Web App.
* **Interaction:** Web UI with minimal sign-in.
* **Needs:** Reproducible, recipe-first execution without writing Python.

### 3. Tree Safety Expert (Secondary)
* **Goal:** Standardized assessments (pull tests, tomography).
* **Interaction:** Predefined workflows, stable reports.

## Success Signals
A user can take **raw device exports** + a **filled metadata package** and get:
1.  A validated, queryable experiment database.
2.  Full-resolution Parquet datasets with documented units.
3.  Publication-ready plots/tables under `results_root`.
4.  A Web App user can sign in, provision a Workspace, and run a Recipe to produce outputs.
...without ever modifying the original raw input files.

## Non-Goals
* Real-time streaming / IoT dashboards.
* Replacing general-purpose stats tools (we prepare the data).
* Strict OGC SensorThings API compliance (we export to it, we don't use it as internal schema).
* Enterprise identity management, multi-tenant permissions, and SSO (beyond MVP).
