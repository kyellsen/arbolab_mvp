# SensorThings API (STA) / OData Export Facade

## Purpose and Scope
This document defines how ArboLab can expose an optional SensorThings API (STA)
/ OData facade for interoperability.

STA is not ArboLab's internal core schema. The STA facade is derived from the
canonical domain model and is allowed to be implemented as projections and/or
DuckDB views.

## Scope of the Facade
The STA facade focuses on:
- metadata navigation (Things, Sensors, ObservedProperties, Datastreams,
  FeatureOfInterest, Locations)
- limited observation access for preview and downsampling

The STA facade is explicitly not designed for:
- full-resolution observation access (billions of rows)
- analytics workloads (joins, windows, statistics, mixed models)

Those remain Parquet/DuckDB-first and are served through the `Lab` API.

## Mapping Rules
### Standard Fields vs Domain Extensions
- Standard STA fields are mapped from ArboLab core entities.
- Additional ArboLab-specific fields must not appear as new top-level fields in
  STA responses.
- Additional fields are emitted under `properties` using a namespaced object,
  for example:
  - `properties.arbolab.project_id`
  - `properties.arbolab.tags`
  - `properties.arbolab.domain_ids`

### Identifier Strategy
- Exported STA entities must use stable identifiers.

## FeatureOfInterest (FOI) Guidance
FOI expresses what observations are "about".
- FOI may map to a Thing, a derived spatial feature, or a domain concept used in
  analysis.

## Observations (Preview / Downsample Only)
STA observations, if exposed, must be constrained:
- preview windows only, or downsampled representations
- bounded payload sizes and strict server-side limits
- no promise of full-resolution completeness

Full-resolution retrieval and analytics remain in the `Lab` API.

## References
- SensorThings API PDF: `docs/requirements/SensorThings_v1.1.pdf`
- `docs/specs/data-model.md`
- `docs/specs/api.md`
