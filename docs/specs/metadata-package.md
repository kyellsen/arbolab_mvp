# Metadata Package Specification

**Binding Rules**: See `../../AGENTS.md`.

## 1. Structure
ArboLab uses the **Frictionless Tabular Data Package** standard.

### Directory Layout
Located at `input_root/<experiment-input>/`:

```text
metadata/
  datapackage.json  (Descriptor)
  *.csv             (Resources)
ls3/                (Raw sensor data)
...
```

## 2. Descriptor (`datapackage.json`)

**MUST** act as the manifest for all tabular resources to be imported.

### Required Fields
- `profile`: `"tabular-data-package"`
- `name`: slug-case string.
- `resources`: List of resource objects.

### Resource Object Contract
Each resource in `resources[]` MUST define:
- `path`: Relative path to CSV (no `..` traversal).
- `schema`:
    - `fields`: List of columns (`name`, `type`).
    - `primaryKey`: Unique identifier column(s).
    - `foreignKeys`: **Required** for referential integrity (e.g., linking `run_id` to `runs.id`).

## 3. CSV Conventions
- **Encoding**: UTF-8.
- **Delimiter**: Comma (`,`).
- **Line Endings**: `\n` preferred.
- **Timestamps**: ISO 8601 with Offset (UTC recommended).
- **Decimals**: Point (`.`).

## 4. Validation Rules
The Lab Importer MUST enforce:
1. **Schema Check**: CSV content matches JSON `schema`.
2. **Integrity Check**: Foreign Keys resolve to existing IDs in referenced resources.
3. **No Magic**: Unreferenced CSVs are ignored.
