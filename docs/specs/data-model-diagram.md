# Domain Model Diagram (Mermaid)

## Purpose
This document provides a checkable Mermaid ER diagram of the ArboLab data model.
It is intended to review entity relationships, cardinalities (one vs many), and
core relationships and cardinalities.

## Notes
- The diagram uses table-level names (snake_case) with the `core_` prefix for
  canonical workspace tables.
- `obs_observations` is an external/view-like entity backed by Parquet (no
  canonical relational table).
- Some attribute lists are intentionally minimal and focus on keys and
  join-critical fields.

## Canonical Core Model (ArboLab)
```mermaid
erDiagram
  core_projects {
    int id PK
  }
  core_experiments {
    int id PK
    int project_id FK
  }

  %% Experiment design and execution
  core_experimental_units {
    int id PK
    int project_id FK
    int thing_id FK
  }
  core_treatments {
    int id PK
    int project_id FK
  }
  core_treatment_applications {
    int id PK
    int experiment_id FK
    int treatment_id FK
    int thing_id FK
    datetime start_time
    datetime end_time
  }
  core_runs {
    int id PK
    int experiment_id FK
    datetime start_time
    datetime end_time
  }
  core_sensor_deployments {
    int id PK
    int experiment_id FK
    int experimental_unit_id FK
    int sensor_id FK
    datetime start_time
    datetime end_time
  }

  %% Assets and measurement metadata
  core_things {
    int id PK
    int project_id FK
    int location_id FK
    string kind
  }
  core_trees {
    int id PK
    int species_id FK
  }
  core_cables {
    int id PK
  }
  core_tree_species {
    int id PK
  }
  core_locations {
    int id PK
  }
  core_sensor_models {
    int id PK
  }
  core_sensors {
    int id PK
    int project_id FK
    int sensor_model_id FK
  }

  %% Stream semantics
  core_observed_properties {
    int id PK
  }
  core_units_of_measurement {
    int id PK
  }
  core_datastreams {
    int id PK
    int sensor_deployment_id FK
  }
  core_datastream_channels {
    int id PK
    int datastream_id FK
    int observed_property_id FK
    int unit_of_measurement_id FK
    int channel_index
  }

  %% Persistence
  core_data_variants {
    int id PK
    int datastream_id FK
    string variant_name
  }

  %% Observations are Parquet-first; this is a view/external table, not a canonical relational table.
  obs_observations {
    int id PK
    int variant_id FK
    datetime timestamp
  }

  %% Project/experiment structure
  core_projects ||--o{ core_experiments : contains
  core_projects ||--o{ core_experimental_units : owns
  core_projects ||--o{ core_treatments : defines
  core_projects ||--o{ core_things : owns
  core_projects ||--o{ core_sensors : owns

  core_things ||--o{ core_experimental_units : references

  core_experiments ||--o{ core_runs : groups
  core_experiments ||--o{ core_sensor_deployments : uses
  core_experiments ||--o{ core_treatment_applications : applies

  core_experimental_units ||--o{ core_sensor_deployments : hosts
  core_sensors ||--o{ core_sensor_deployments : installs

  core_treatments ||--o{ core_treatment_applications : instantiates
  core_things ||--o{ core_treatment_applications : targets

  %% Asset subtypes (optional)
  core_things ||--o| core_trees : subtype
  core_things ||--o| core_cables : subtype
  core_tree_species o|--o{ core_trees : classifies
  core_sensor_models ||--o{ core_sensors : classifies

  %% Spatial relationships (current location only)
  core_locations o|--o{ core_things : locates

  %% Measurement stream relationships
  core_sensor_deployments ||--o{ core_datastreams : produces
  core_datastreams ||--|{ core_datastream_channels : has
  core_observed_properties ||--o{ core_datastream_channels : defines
  core_units_of_measurement ||--o{ core_datastream_channels : uses

  core_datastreams ||--o{ core_data_variants : persists
  core_data_variants ||--o{ obs_observations : has
```
