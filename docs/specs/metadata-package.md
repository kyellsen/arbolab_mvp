# Experiment Metadata Package (Frictionless Data Package)

## Purpose and Scope
This document defines ArboLab's **interchange format** for experiment metadata:
an **offline-first metadata package** that can be created and edited with
general-purpose tools (spreadsheet editors, CSV tools, text editors) and then
validated and imported into a Lab workspace.

ArboLab uses the **Frictionless Data Package** standard as the normative
container format:
- descriptor: `datapackage.json`
- resources: tabular CSV files referenced by the descriptor

This spec defines the **ArboLab constraints** on top of the Frictionless
standard (file locations, naming, required fields, and validation rules). It
does not restate the Frictionless specification.

## References (External)
- Frictionless Data Package: https://specs.frictionlessdata.io/data-package/
- Frictionless Tabular Data Package: https://specs.frictionlessdata.io/tabular-data-package/

## Location and Directory Layout
ArboLab operates on an input-only, read-only **experiment input directory**
provided by the user under `input_root`.

The directory contains:
- `metadata/`: the Frictionless Data Package (descriptor + tabular resources)
- one subdirectory per sensor/source type (for example `ls3/`, `tms/`) containing
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

Template generation:
- The documentation template generator MUST scaffold this structure under
  `results_root/templates`.
- Template generation and metadata package exports MUST NOT write to
  `input_root`. Users copy the generated template into `input_root` when ready.

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
- timestamps MUST be ISO 8601 strings with timezone offset (for example
  `2026-01-07T12:34:56Z`)
- decimals MUST use `.` as the decimal separator
- physical units MUST be represented explicitly as values in the appropriate
  metadata tables (see `docs/specs/units-and-data-dictionary.md`)

## Extensibility (Plugins)
Plugins MAY extend the metadata package by adding additional resources.

Rules:
- Plugin-added resources MUST use a namespaced resource name to avoid collisions
  (recommended: `<plugin_entry_point>__<resource>`).
- The core importer MUST ignore unknown resources unless a responsible plugin is
  enabled and declares support for them.

