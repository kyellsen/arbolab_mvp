# Storage Format and Layout

## Storage Roots
ArboLab operates on three explicit storage roots configured via `DataPaths`:
- `input_root` is the read-only raw data area for immutable sensor data files.
- `workspace_root` is the internal working area for mutable state (DuckDB, Parquet, intermediate artifacts, logs).
- `results_root` is the write-only target for publication outputs (plots, LaTeX, exports).
- Documentation templates are written under `results_root/templates` and never under `input_root`.

## Default Layout from base_root
A single `base_root` may derive sensible defaults:

```text
base_root/
├── data/       -> input_root
├── workspace/  -> workspace_root
└── results/    -> results_root
```

Rules:
- `data` and `results` are siblings of `workspace`.
- All three roots may live under a common `base_root`, but this is optional.
- There is no default that silently places input or results inside `workspace_root`; roots are explicit or derived in a controlled way.

## Workspace Layout
Within `workspace_root`, the core expects internal subtrees with lazy creation semantics:
- `storage/variants/` for complete Datastream datasets grouped by variant and datastream identifiers.
- Additional folders such as `logs/` or `tmp/` as needed.

## Persistence and Data Storage
- Metadata is stored in DuckDB tables under `workspace_root` (for example `workspace_root/db/`) via SQLAlchemy declaratives.
- Plugin tables extend core models, enabling joins between protocol data and time-series references, and live inside the same workspace database.
- Time-series data is ingested lazily with Polars/PyArrow and stored as Parquet files under `workspace_root/storage/variants/` (default `data.parquet` per variant), then registered with DuckDB.
- Persisted datasets may include a small JSON sidecar (for example `dataset.json`) that documents columns and units for portability.
- All internal files produced by the pipeline reside within `workspace_root`.
- Raw input is read from `input_root` only; no component mutates files there.
- Analysis results for publication are written to `results_root` (LaTeX, plots, exports).

## Data Variants and Storage Contracts
- `DataVariant` is the SQLAlchemy entity describing a persisted dataset variant for a single Datastream. It captures:
  - datastream identifier
  - variant name
  - logical layout (`format`, currently `wide`)
  - physical representation (`data_format`, typically `parquet`)
  - time column and column specifications
  - on-disk files, row/column counts, file sizes
  - first and last timestamps
  - `data_path` and `data_files` as workspace-relative strings
- `RAW_DATA_VARIANT_NAME` is the canonical label for unprocessed sensor data; additional variants (for example `processed`) may coexist.
- The variant store maintains the `variants` layer defined by the workspace configuration.
- Variant directories follow this hierarchy:

```text
storage/variants/
  project_id=<id>/
  datastream_id=<id>/
  variant=<name>/
```

Segments with `None` identifiers are omitted. Plugins can rely on zero-padded, explicit `key=value` segments and always append `variant=<name>` as the terminal directory. Globs like `storage/variants/**/variant=raw/*.parquet` match all raw exports.
- The variant store prepares variant directories on demand (for example `prepare_datastream_variant_directory`), validates that stored paths never escape `workspace_root`, and returns both absolute and workspace-relative paths when resolving existing variants.
- Plugin ingestion contract: device plugins obtain their write location from the variant store, persist Parquet (or a negotiated format) inside the returned directory, and populate a matching `DataVariant` entry that includes the produced `data_files` metadata. The default logical layout is wide (timestamp column plus sensor value columns). Introducing new logical layouts requires coordinating the `format` label with the core.
- Results contract: plotting, LaTeX export, and table/CSV export utilities resolve output locations under `results_root` through the `ResultsLayout` (and may use `ResultsWriter` to prepare directories). The pipeline never treats `results_root` artifacts as input data and never registers them as `DataVariant` data.
