# Metadata Package & Import Specification

**Binding Rules**: See `../../AGENTS.md`.

## Purpose and Scope
This document defines ArboLab's **interchange format** for experiment metadata:
an **offline-first metadata package** that can be created and edited with
general-purpose tools (spreadsheet editors, CSV tools, text editors) and then
validated and imported into a Lab workspace.

It also defines the **supported pathways** for bringing this metadata into the Lab.

ArboLab uses the **Frictionless Data Package** standard as the normative
container format:
- descriptor: `datapackage.json`
- resources: tabular CSV files referenced by the descriptor

## References (External)
- Frictionless Data Package: https://specs.frictionlessdata.io/data-package/
- Frictionless Tabular Data Package: https://specs.frictionlessdata.io/tabular-data-package/

## Import Pathways

### Supported Pathways
- **Documentation Package Import**: A fully valid Frictionless Data Package descriptor
  (`metadata/datapackage.json`) and its resources under
  `input_root/<experiment-input>/metadata`.

### Non-Goals
- Direct mapping from ad-hoc/legacy sources (spreadsheets, raw CSVs) into the Lab
  database without first producing a valid metadata package.
- The standard prevents "magic" import logic; legacy data *must* be converted to
  a canonical package first.

## Location and Directory Layout
ArboLab operates on an input-only, read-only **experiment input directory**
provided by the user under `input_root`.

The directory contains:
- `metadata/`: the Frictionless Data Package (descriptor + tabular resources)
- one subdirectory per sensor/source type (e.g., `ls3/`, `tms/`) containing
  raw sensor exports in their native formats

Example layout:

```text
<experiment-input>/
  metadata/
    datapackage.json
    *.csv
  ls3/
    ...
  tms/
    ...
```

**Template Generation**:
- The documentation template generator MUST scaffold this structure under
  `results_root/templates`.
- Generation and exports MUST NOT write to `input_root`.

## Descriptor File: `datapackage.json`
The metadata package descriptor MUST be:
- named exactly `datapackage.json`
- located at `<experiment-input>/metadata/datapackage.json`
- valid UTF-8 JSON

The descriptor MUST declare a **Tabular Data Package**:
- `profile` MUST be `tabular-data-package`

The descriptor MUST include:
- `name` (Frictionless package name, lowercase slug)
- `version` (ArboLab metadata package schema version, semantic version string)
- `resources` (list of tabular resources)

The descriptor SHOULD include:
- `title` (human-readable experiment title)
- `created` (ISO 8601 timestamp)
- `licenses` (package license(s) for sharing/open data contexts)

## Resources
### Resource Shape
Every ArboLab metadata resource MUST:
- be declared in `resources[]` in `datapackage.json`
- be a CSV file located under `<experiment-input>/metadata/`
- use a relative `path` without path traversal segments (no `..`)
- include a `schema` with:
  - `fields[]` (names + types)
  - `primaryKey` for the table identifier column(s)

Resources SHOULD include `foreignKeys` in their schemas to enable referential
integrity validation before import.

### CSV Conventions
All CSV resources MUST:
- be encoded as UTF-8
- include a header row
- use comma (`,`) as delimiter
- use `\n` line endings (tools MAY tolerate `\r\n`, but generated templates use `\n`)

### Time and Units Conventions
To avoid locale and ambiguity issues:
- timestamps MUST be ISO 8601 strings with timezone offset (e.g.,
  `2026-01-07T12:34:56Z`)
- decimals MUST use `.` as the decimal separator
- physical units MUST be represented explicitly as values in the appropriate
  metadata tables (see `docs/specs/data-model.md`)

## Extensibility (Plugins)
Plugins MAY extend the metadata package by adding additional resources.

Rules:
- Plugin-added resources MUST use a namespaced resource name to avoid collisions
  (recommended: `<plugin_entry_point>__<resource>`).
- The core importer MUST ignore unknown resources unless a responsible plugin is
  enabled and declares support for them.

