# Data Variants and Ingestion

## Purpose and Scope
This document defines the contract for ingesting raw sensor exports into queryable datasets stored under `workspace_root`.

## Input Is Read-Only
- Raw sensor inputs are read only from `input_root`.
- The pipeline must not modify, delete, or rewrite files in the experiment input directory under `input_root`.

## Source Discovery and File Linking
- Before ingesting time-series values, ArboLab must be able to associate metadata entities (Runs, Sensors, SensorDeployments) with the physical raw files in the experiment input directory under `input_root`.
- The file linking logic is sensor-type specific and is expected to be implemented by plugins.
- Linking must be validated before ingestion proceeds (missing files, ambiguous matches, inconsistent identifiers).
- When linking fails, ArboLab must provide actionable diagnostics instead of producing partial ingested state.
- Linking and ingestion are executed only for plugins explicitly enabled in configuration.

## Variants as the Canonical Workspace Dataset
- Ingested time-series datasets must be persisted as DataVariants inside `workspace_root`.
- Each persisted dataset must have:
  - a stable identifier in the Lab database,
  - a `variant_name` describing its processing stage (for example `raw`, `cleaned`, `derived`),
  - a physical representation stored under the workspace storage layout.
- Each DataVariant is anchored to a single Datastream identifier (see `docs/specs/data-model.md`).
- Variants must be stored in a format suitable for efficient query and reproducibility (default: Parquet).

## Variant Persistence API
- The core must provide a standard facility (`VariantStore`) for persisting variants that:
  - prepares a workspace directory for the variant,
  - writes the dataset files into the workspace,
  - records the resulting metadata in the Lab database.

## Safety and Path Constraints
- All persisted variant paths must remain within `workspace_root`.
- Variant persistence must not write to `input_root` or `results_root`.

## Re-ingestion Behavior
- Re-running ingestion against the same experiment input directory under `input_root` must be safe.
- Re-ingestion must not silently mutate existing DataVariants.
- If the resulting dataset is identical, the existing DataVariant must be reused and reported.
- If the resulting dataset differs, ingestion must create a new DataVariant (for example by using an explicitly versioned variant name) and must not overwrite the previous dataset in place.

## References
- Storage layout is defined in `docs/architecture/storage-format.md`.
