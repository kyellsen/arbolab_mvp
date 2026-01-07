# Storage & Data Layout

## Storage Roots
ArboLab operates on three explicit roots. No default silently places inputs or results inside workspace.

1.  **`input_root` (Read-Only):** Immutable raw sensor data files.
2.  **`workspace_root` (R/W):** Internal state (DuckDB, Parquet variants, logs).
3.  **`results_root` (Write-Only):** Publication outputs (Plots, LaTeX, Exports).

## Workspace Structure
Managed internal structure within `workspace_root`:

* `db/`: DuckDB persistence (SQLAlchemy models).
* `storage/variants/`: Parquet data, grouped by project/datastream.
* `logs/`, `tmp/`: Runtime ephemerals.

## Data Variants (`DataVariant`)
Measurements are stored as **Variants** (e.g., `raw`, `processed`).

* **Format:** Parquet (default `wide` layout: timestamp + sensor columns).
* **Metadata:** Stored in DuckDB (`DataVariant` entity).
* **Pathing:** `storage/variants/project_id=X/datastream_id=Y/variant=Z/`.
* **Logic:**
    * `RAW_DATA_VARIANT_NAME` is the canonical entry point.
    * Plugin ingestion writes Parquet here, then registers metadata in DuckDB.
    * Internal paths are strictly relative to `workspace_root`.

## Persistence Contract
* **DuckDB:** Stores relational metadata, configuration state, and provenance.
* **Parquet:** Stores high-volume time-series data.
* **Results:** Written via `ResultsLayout` / `ResultsWriter` only to `results_root`.