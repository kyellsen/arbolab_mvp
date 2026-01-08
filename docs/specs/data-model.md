# Data Model & Persistence Specification

**Terminological Binding**: Strict adherence to `../requirements/glossary.md`.

## 1. Entity Relationship Diagram

Normative schema for `core_` tables.

```mermaid
erDiagram
  %% PROJECT CONTEXT
  core_projects ||--o{ core_experiments : defines
  core_projects ||--o{ core_things : owns
  core_projects ||--o{ core_sensors : owns
  core_projects ||--o{ core_treatments : defines
  core_projects ||--o{ core_experimental_units : defines

  %% EXPERIMENTAL CONTEXT
  core_experiments ||--o{ core_runs : groups
  core_experiments ||--o{ core_sensor_deployments : context_for
  core_experiments ||--o{ core_treatment_applications : context_for

  %% ANALYTICAL CONTEXT
  core_experimental_units ||--o{ core_sensor_deployments : hosts
  core_things ||--o{ core_experimental_units : participates_in

  %% THINGS & LOCATIONS
  core_locations ||--o{ core_things : locates
  core_things ||--|| core_trees : is_a
  core_things ||--|| core_cables : is_a
  core_tree_species ||--o{ core_trees : classifies

  %% TREATMENTS
  core_treatments ||--o{ core_treatment_applications : applied_as
  core_things ||--o{ core_treatment_applications : subjected_to

  %% DEPLOYMENT & SENSORS
  core_sensors ||--o{ core_sensor_deployments : installed_as
  core_sensor_models ||--o{ core_sensors : classifies

  %% DATASTREAM & STORAGE
  core_sensor_deployments ||--o{ core_datastreams : produces
  core_datastreams ||--o{ core_data_variants : persists
  core_datastreams ||--o{ core_datastream_channels : defines
  core_observed_properties ||--o{ core_datastream_channels : measures
  core_units_of_measurement ||--o{ core_datastream_channels : expressed_in

  %% VIRTUAL / PARQUET
  core_data_variants ||--o{ parquet_observations : describes
```

## 2. Relational Schema (DuckDB)

Location: `workspace_root/db/arbolab.duckdb` (Main DB)

### 2.1 Physical Perspective (Assets)
| Table | Column | Type | Constraints | Description |
|:---|:---|:---|:---|:---|
| `core_locations` | `id` | INTEGER | PK | Spatial reference. |
| | `name` | VARCHAR | | |
| `core_things` | `id` | INTEGER | PK | Stable object identity. |
| | `project_id` | INTEGER | FK | |
| | `location_id` | INTEGER | FK | |
| | `kind` | VARCHAR | | Discriminator ('tree', 'cable', ...). |
| `core_trees` | `id` | INTEGER | PK, FK | **SubType** of Thing. |
| | `species_id` | INTEGER | FK | |
| `core_tree_species` | `id` | INTEGER | PK | |
| | `name` | VARCHAR | | |
| `core_cables` | `id` | INTEGER | PK, FK | **SubType** of Thing. |
| `core_sensor_models` | `id` | INTEGER | PK | |
| | `model_name` | VARCHAR | | |
| `core_sensors` | `id` | INTEGER | PK | |
| | `project_id` | INTEGER | FK | |
| | `sensor_model_id` | INTEGER | FK | |

### 2.2 Experimental Perspective (Campaigns)
| Table | Column | Type | Constraints | Description |
|:---|:---|:---|:---|:---|
| `core_projects` | `id` | INTEGER | PK | |
| | `name` | VARCHAR | | |
| `core_experiments` | `id` | INTEGER | PK | |
| | `project_id` | INTEGER | FK | |
| `core_runs` | `id` | INTEGER | PK | |
| | `experiment_id` | INTEGER | FK | |
| | `start_time` | TIMESTAMP | | |
| | `end_time` | TIMESTAMP | | |
| `core_experimental_units` | `id` | INTEGER | PK | Statistical subject. |
| | `project_id` | INTEGER | FK | |
| | `thing_id` | INTEGER | FK | Optional link to Thing. |
| `core_sensor_deployments` | `id` | INTEGER | PK | **Central Context Entity.** |
| | `experiment_id` | INTEGER | FK | |
| | `experimental_unit_id` | INTEGER | FK | |
| | `sensor_id` | INTEGER | FK | |
| | `start_time` | TIMESTAMP | | |
| | `end_time` | TIMESTAMP | | |
| | `mounting` | JSON | | |

### 2.3 Analytical Perspective (Logic)
| Table | Column | Type | Constraints | Description |
|:---|:---|:---|:---|:---|
| `core_treatments` | `id` | INTEGER | PK | Abstract condition. |
| | `project_id` | INTEGER | FK | |
| `core_treatment_applications` | `id` | INTEGER | PK | Concrete application. |
| | `experiment_id` | INTEGER | FK | |
| | `treatment_id` | INTEGER | FK | |
| | `thing_id` | INTEGER | FK | |
| | `start_time` | TIMESTAMP | | |
| | `end_time` | TIMESTAMP | | |

### 2.4 Data Perspective (Storage)
| Table | Column | Type | Constraints | Description |
|:---|:---|:---|:---|:---|
| `core_datastreams` | `id` | INTEGER | PK | Logical container. |
| | `sensor_deployment_id` | INTEGER | FK | |
| `core_observed_properties` | `id` | INTEGER | PK | e.g. "temperature". |
| `core_units_of_measurement` | `id` | INTEGER | PK | e.g. "degree Celsius". |
| `core_datastream_channels` | `id` | INTEGER | PK | Channel definition. |
| | `datastream_id` | INTEGER | FK | |
| | `observed_property_id` | INTEGER | FK | |
| | `unit_of_measurement_id`| INTEGER | FK | |
| | `channel_index` | INTEGER | | |
| `core_data_variants` | `id` | INTEGER | PK | Physical Dataset Metadata. |
| | `datastream_id` | INTEGER | FK | |
| | `variant_name` | VARCHAR | | e.g., 'raw'. |
| | `format` | VARCHAR | | 'wide'. |
| | `data_format` | VARCHAR | | 'parquet'. |
| | `column_specs` | JSON | | |
| | `data_path` | VARCHAR | | Relative path to files. |
| | `data_files` | JSON | | List of filenames. |
| | `row_count` | INTEGER | | |
| | `first_timestamp` | TIMESTAMP | | |
| | `last_timestamp` | TIMESTAMP | | |

## 3. Column Metadata & Units

The `column_specs` JSON field in `core_data_variants` is the source of truth for all column metadata.

### 3.1 JSON Schema (ColumnSpec)
Each entry in the `column_specs` map must adhere to:

```json
{
  "name": "inclination_x",      // (Required) Workspace column name
  "dtype": "float64",           // (Required) Logical type
  "unit": "deg",                // (Required) UCUM identifier (or '1' for dimensionless)
  "description": "...",         // (Required) Human readable context

  // Display Metadata (Optional but Recommended)
  "label": "Inclination X",     // Short display label
  "symbol": "phi",              // Math symbol (no $ delimiters)
  "symbol_latex": "\\phi",      // Specific LaTeX override
  "unit_symbol": "°",           // Display symbol
  "unit_siunitx": "\\degree"    // LaTeX siunitx string
}
```

### 3.2 Unit Propagation Rules
- **Raw Ingestion**: Plugins MUST map raw device units to valid `ColumnSpec` entries.
- **Derivation**: Derived datasets MUST update unit and label. Dimensionless columns use `unit: "1"`.
- **Export**:
    - Plots use `label` + `unit_symbol` (e.g., "Inclination X [°]").
    - LaTeX uses `symbol_latex` + `unit_siunitx`.

## 4. Observation Storage (Parquet)

### 4.1 Schema Expectation (Wide Layout)
- **Format**: Parquet.
- **Location**: Referenced by `core_data_variants.relative_path`.
- **Columns**:
    - `timestamp`: Timestamp (UTC), Sorted.
    - `[metric_1]`: Sensor Value.
    - `[metric_n]`: Sensor Value.

### 4.2 Querying Strategy
DuckDB `read_parquet()` + Join `core_data_variants` -> `core_datastreams` -> `core_sensor_deployments`.
