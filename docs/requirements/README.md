# Requirements & Vision

**Binding Rules:** See `../../AGENTS.md`.

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

### 2. Tree Safety Expert (Secondary)
* **Goal:** Standardized assessments (pull tests, tomography).
* **Interaction:** Predefined workflows, stable reports.

### 3. SaaS Backend (Future)
* **Goal:** Run workflows as services. **Out of MVP scope.**

## Success Signals
A user can take **raw device exports** + a **filled metadata package** and get:
1.  A validated, queryable experiment database.
2.  Full-resolution Parquet datasets with documented units.
3.  Publication-ready plots/tables under `results_root`.
...without ever modifying the original raw input files.

## Non-Goals
* Real-time streaming / IoT dashboards.
* Replacing general-purpose stats tools (we prepare the data).
* Strict OGC SensorThings API compliance (we export to it, we don't use it as internal schema).