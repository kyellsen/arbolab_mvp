# Requirements Overview (Vision & Scope)

## Purpose
Capture the problem-space requirements from a domain/user perspective without implementation details.
This is the entry point for requirements.

This file is the single source of truth for the requirements overview (vision, scope, and prioritisation) within `docs/requirements/`.

## Reading Map
- `docs/requirements/glossary.md` (terms, definitions, example sentences)
- `docs/requirements/user-stories/` (user stories with example scenarios)

## Personas and Usage Modes
ArboLab is designed for three primary usage modes. The product will be built in phases; the modes below are used to guide scope and prioritization.

### Persona 1 (Primary): Researcher / Student (Notebook & Pipeline)
- Profile: scientific user with statistics and domain expertise.
- Goal: explore, process, and analyze tree sensor data with maximal flexibility.
- Typical interaction: Jupyter notebooks and custom data-science pipelines.
- Needs: composable APIs, reproducibility, inspectable intermediate results, and the ability to extend workflows.

### Persona 2 (Secondary): Tree Safety Expert (Standard Workflows)
- Profile: practitioner focused on standardized assessments (for example pulling tests / load tests, acoustic tomography).
- Goal: run established analysis workflows and obtain interpretable results (stability / fracture safety indicators) with minimal customization.
- Typical interaction: notebook-based workflows composed of predefined analysis blocks.
- Needs: guided workflows, sane defaults, and clear outputs; limited need for experimental exploration.

### Persona 3 (Future): SaaS Backend (Web Frontend Integration)
- Profile: ArboLab used as a backend behind a web UI for Persona 2-like workflows.
- Goal: execute workflows as services (potentially at scale) and expose results to a UI.
- Typical interaction: service/API integration (no notebooks required).
- Needs: stable boundaries, replaceable components, and a path to job-style execution; not a near-term feature target.

### Phasing
- MVP focus: Persona 1.
- Next: Persona 2 built on Persona 1 capabilities.
- Later: Persona 3 constraints considered to avoid architectural dead-ends, but features are deferred.

## Vision
ArboLab makes full-resolution experimental sensor data analysis reproducible and
ergonomic:
- raw device exports and experiment metadata become a queryable, joinable, and
  auditable workspace,
- analyses operate on observations,
- workflows remain modular and extensible through plugins,
- interoperability is supported through explicit file-based exports (for example
  CSV/Parquet) without constraining the core.

## Problem Statement
Researchers and practitioners routinely collect high-frequency sensor data in
field and lab experiments. The pain points are:
- observation scale (millions to billions of rows) makes naive tooling unusable,
- metadata is fragmented (spreadsheets, ad-hoc naming, device-specific exports),
- linking execution context (runs, treatments, sensor mounts) to time-series
  segments is brittle,
- reproducibility is poor when intermediate datasets and assumptions are not
  persisted and documented.

## Target Users / Roles
- Primary: researcher/student using notebooks and custom pipelines.
- Secondary: practitioner using standardized workflows built on the same core.
- Plugin developer: implements device parsers and ingestion logic.

## Top Use Cases (List)
- Create/open a Lab workspace and configure storage roots.
- Generate an offline metadata documentation package, fill it in the field, and
  import it with validation.
- Link raw sensor files to metadata (runs, deployments) and ingest them into
  standardized workspace variants.
- Run analytics queries across many runs/streams at full resolution and
  materialize derived datasets for downstream modelling.
- Produce publication-ready results (plots, tables, exports) under `results_root`.

## Goals
- Analytics-first: support high-volume, join-heavy analysis workloads.
- Domain-first: model experiments in domain language (things, sensors, projects, experiments, runs, treatments,
  treatment applications, deployments) rather than external standards.
- Reproducibility: persist intermediate datasets (variants) with
  sufficient metadata to re-run and compare analyses.
- Modularity: isolate device-specific logic in plugins with explicit extension
  points.
- Interoperability: keep file-based exports feasible without forcing the core
  into a lowest-common-denominator schema.

## Non-Goals
- Real-time streaming ingestion and online serving for IoT dashboards.
- Multi-tenant SaaS runtime in the MVP phase.
- Replacing general-purpose statistics tooling; ArboLab focuses on preparing and
  executing reproducible data pipelines and producing model-ready tables.
- Event sourcing, domain events, or an audit log of metadata edits (edits may overwrite prior values in the MVP).

## Scope
- In scope:
  - offline-first experiment metadata packages and validated import
  - ingestion into Parquet-first workspace variants
  - DuckDB-backed analytics queries and derived dataset materialization
  - results outputs under `results_root`
- Out of scope:
  - storing canonical observations as row-based relational tables
  - exposing full-resolution observation access through web APIs
  - production-grade web UI in the MVP phase

## Success Signals (Informal)
- A user can go from raw device exports + a filled metadata package to:
  - validated, queryable experiment structure,
  - full-resolution Parquet datasets with documented columns/units,
  - repeatable analysis tables (per-run summaries and cross-run derived tables),
  - publication-ready outputs written to `results_root`,
  without modifying the original raw input directory.

## Constraints / Risks (High Level)
- Data volume and performance: full-resolution workflows require disciplined
  storage formats, limits, and query patterns.
- Schema evolution: metadata and query specs must remain versionable without
  breaking reproducibility.

## Notes
Concrete, testable contracts and nonfunctional/process constraints live in `docs/specs/`.

Storage root and workspace/path conventions live in:
- `docs/specs/api.md`
- `docs/architecture/storage-format.md`

Examples for offline documentation packages and metadata import live in:
- `docs/requirements/user-stories/US-002-offline-experiment-documentation-package.md`
- `docs/specs/metadata-import.md`
