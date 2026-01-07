# Domain Data Model Specification

## Purpose and Scope

This document specifies the **canonical persistence model** for ArboLab.
It defines tables, relationships, and storage rules derived from the
**normative Ubiquitous Language** defined in:

- `docs/requirements/glossary.md`

This document **MUST NOT redefine domain terminology**.
All terms are used exactly as defined in the glossary.

The specification focuses on:
- relational persistence of domain metadata,
- linkage between execution context and measurement data,
- analytics-first storage and querying using DuckDB and Parquet.

---

## Orientation: Domain-First, Analytics-First

ArboLab is designed for **high-volume analytical workflows**:

- Observations are stored **Parquet-first** at full resolution.
- Analytics (joins, windows, statistics, mixed models) run in **DuckDB**.
- Domain metadata and execution context are persisted relationally.
- The internal schema is optimized for analysis and reproducibility,
  not for external API compatibility.

---

## Normative Terminology

All domain terms used in this document are defined in:

- `docs/requirements/glossary.md`

If a term is not defined there, it **MUST NOT** be introduced here.

---

## Domain Perspectives

The persistence model reflects four conceptual perspectives:

1. **Physical / Real-World**
2. **Experimental / Campaign**
3. **Analytical / Statistical**
4. **Data / Observation**

Perspectives are **conceptual lenses**, not technical layers.
Tables are grouped by primary responsibility, not by storage mechanism.

---

## Canonical Workspace Schema

This specification describes the canonical workspace schema.
Table names are **domain-driven** and do not encode technical layers
or external standards.

Views or derived schemas may exist for specific use cases but are not
the source of truth.

---

## Physical / Real-World Entities

These entities represent persistent real-world objects and assets.

### Things
- `things`
- Optional subtypes:
  - `trees`
  - `cables`

Things are identity-stable and reusable across experiments.

### TreeSpecies
- `tree_species`

TreeSpecies classify Trees.
They are reusable and may be shared across projects.

### Locations
- `locations`

Locations describe current spatial information associated with Things.
Location history is out of scope in the canonical model.

### Sensors
- `sensor_models`
- `sensors`

**SensorModel**
- describes sensor capabilities (supported channels, nominal units,
  sampling limits),
- is reusable and global.

**Sensor**
- represents a concrete physical device,
- references exactly one SensorModel,
- is portable and reusable across deployments.

---

## Experimental / Campaign Entities

These entities structure measurement campaigns and executions.

### Projects
- `projects`

Projects define long-lived research contexts.
They group experiments, reusable assets, and metadata.

### Experiments
- `experiments`

Experiments are **time-bounded measurement campaigns** within a Project.
They define temporal scope but not simultaneity.

### Runs
- `runs`

Runs represent **concrete execution sessions** within an Experiment.

Normative rules:
- A Run groups measurements belonging to the same execution context.
- A Run does **not** imply perfect temporal synchrony between sensors.
- Sensor clocks may drift or start asynchronously.
- Synchronization quality is descriptive metadata, not a guarantee.

### TreatmentApplications
- `treatment_applications`

TreatmentApplications represent **concrete, time-bounded applications**
of a Treatment to a Thing within an experimental context.

Normative rules:
- Treatments are instantiated **only** via TreatmentApplications.
- TreatmentApplications may overlap Runs and may span Run boundaries.
- Within-subject and mixed designs are represented by multiple
  TreatmentApplications over time.

### SensorDeployments
- `sensor_deployments`

SensorDeployments describe **how a Sensor is installed** on a Thing in the
context of an ExperimentalUnit.

Normative rules:
- SensorDeployments are time-bounded.
- Mounting position, orientation, channel mapping, and effective
  calibration belong to SensorDeployment.
- When a sensor is moved, reconfigured, or remounted, a **new
  SensorDeployment** is created.

---

## Analytical / Statistical Entities

These entities define units of comparison and inference.

### Treatments
- `treatments`

Treatments are **abstract, project-scoped definitions** of experimental
conditions or interventions.

Normative rules:
- Treatments are reusable and are not time-bounded.
- Treatments do not represent concrete events.
- Treatments are instantiated **only** via TreatmentApplications.

### ExperimentalUnits
- `experimental_units`

ExperimentalUnits are **conceptual units of analysis**.

Normative rules:
- ExperimentalUnits define *what is analysed statistically*.
- An ExperimentalUnit is not necessarily a single physical object.
- It may reference a Thing, a part, a configuration, or a combination
  thereof.
- Treatments are associated via TreatmentApplications.
- ExperimentalUnits are identity-stable within their analytical context.

---

## Data / Observation Entities

These entities describe measurement streams and their semantics.

### ObservedProperties
- `observed_properties`

ObservedProperties define **what is measured**, independent of sensor,
unit, or experiment.

### Units of Measurement
- `units_of_measurement`

Units define **how values are represented** numerically.

### Datastreams
- `datastreams`

Datastreams are logical containers for time-ordered observations.

Normative rules:
- A Datastream originates from **exactly one SensorDeployment**.
- Datastreams do not aggregate data from multiple deployments.
- Configuration changes do **not** silently reuse an existing Datastream.

### DatastreamChannels
- `datastream_channels`

DatastreamChannels represent the **smallest semantically unambiguous
measurement unit**.

Each DatastreamChannel binds:
- one ObservedProperty,
- one UnitOfMeasurement,
- to a specific channel position within a Datastream.

Channel order, count, and semantics are fixed for a Datastream.

---

## Analytics Metadata

These entities describe persisted datasets and derived results.

### DataVariants
- `data_variants`

DataVariants describe **immutable persisted variants** of a Datastream
(for example raw or derived).

Normative rules:
- DataVariants are append-only and immutable.
- Reprocessing creates a new DataVariant.
- Changes in SensorDeployment configuration may result in:
  - a new DataVariant, or
  - a new Datastream, depending on scope.

---

## Observation Storage (Parquet-First)

Observations are **not** stored as canonical relational tables.

Rules:
- Observations are stored as Parquet datasets.
- DuckDB provides relational access via views or external tables.
- There is no canonical `observations` table.
- Full-resolution analysis is always Parquet/DuckDB-first.

---

## Entities vs. Annotations

ArboLab introduces entities **only when they carry responsibility** that
must be:
- addressed,
- validated,
- historized,
- versioned,
- or joined analytically.

Examples:
- Labels used only for analysis (for example “StemA”, “StemB”) are dataset
  annotations, not core entities.
- Components with lifecycle and metadata (for example Sensors,
  SensorDeployments) are core entities.

---

## Base Fields and Modeling Conventions

Tables SHOULD (but are not required to) share common fields:

- `id` (stable identity)
- `created_at`, `updated_at`
- optional `name`, `description`
- extensibility via `properties` (namespaced JSON)
- optional `tags`

Avoid deep ORM inheritance hierarchies.
Prefer composition and explicit relationships.

---

## References

- `docs/requirements/glossary.md`
- `docs/specs/data-model-diagram.md`
