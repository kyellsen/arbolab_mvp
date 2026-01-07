# Domain Events (Event Storming Lite)

## Purpose
Events define the state transitions of the ArboLab ecosystem. They act as the "Definition of Done" for pipeline stages and specify the minimal required data (payload) to maintain reproducibility.

---

## Event List

### 1. LabWorkspaceOpened
* **Trigger:** User initializes or opens a Lab instance.
* **Source of Truth:** `arbolab.yaml` + Workspace DuckDB.
* **Payload:** `workspace_root`, `config_version`, `enabled_plugins`.
* **"Done" Condition:** Configuration is validated, and the DuckDB session is active.
* **Notes:** Must be idempotent. If the workspace doesn't exist, it is created.

### 2. DocumentationTemplateGenerated
* **Trigger:** User requests an offline metadata template (Frictionless Data Package).
* **Source of Truth:** Filesystem (`results_root/templates/`).
* **Payload:** `project_id`, `experiment_id`, `schema_version`.
* **"Done" Condition:** A valid `datapackage.json` and empty CSV headers exist.
* **Notes:** Templates are for humans to fill in the field/lab.

### 3. MetadataPackageImported
* **Trigger:** User imports a filled-in metadata package.
* **Source of Truth:** Workspace DuckDB (Domain Tables).
* **Payload:** Created/Updated counts for `Things`, `Sensors`, `Runs`, `Deployments`.
* **"Done" Condition:** All relational records are persisted. No broken foreign keys (e.g., a Deployment without a Sensor).
* **Follow-up:** Enables `RawFilesLinked`.

### 4. RawFilesLinked
* **Trigger:** Plugin scans `input_root` for files matching the imported metadata.
* **Source of Truth:** Workspace DuckDB (`FileLink` records).
* **Payload:** `datastream_id` ↔ `file_path` mapping, `checksums` (optional).
* **"Done" Condition:** Every `Datastream` defined in the metadata has at least one unambiguous file reference in `input_root`.
* **Notes:** This step performs no I/O on the file content, only path resolution.

### 5. DataVariantIngested
* **Trigger:** Execution of the ingestion pipeline (Parser + Ingestor).
* **Source of Truth:** Parquet files (`workspace_root`) + `DataVariant` (DuckDB).
* **Payload:** `variant_name` (e.g., 'raw'), `row_count`, `time_range` (min/max), `column_schema`.
* **"Done" Condition:** Parquet files are successfully written, and the metadata record in DuckDB points to the valid relative paths.
* **Notes:** **Crucial for Reproducibility.** Once ingested, the `raw` variant is the immutable source for all further analytics.

### 6. DerivedVariantMaterialized
* **Trigger:** Analytics/Processing step (e.g., filtering, resampling).
* **Source of Truth:** Parquet files + `DataVariant` (DuckDB).
* **Payload:** `parent_variant_id`, `transformation_log`, `new_variant_name`.
* **"Done" Condition:** The derived dataset is stored alongside the raw data.