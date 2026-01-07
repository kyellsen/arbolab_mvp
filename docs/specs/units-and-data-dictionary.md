# Units and Data Dictionary

## Purpose and Scope
This document defines how ArboLab represents units and column metadata across:
- raw ingestion (plugins),
- persisted workspace datasets (DataVariants),
- derived datasets and model outputs,
- downstream exports (plots, LaTeX, tables).

The goal is that every persisted column (raw or derived) carries machine-readable
unit identifiers and sufficient display metadata for consistent labeling.

## Canonical Representation (ColumnSpec)
ArboLab uses `ColumnSpec` entries to document every dataset column.

Required fields:
- `name`: normalised workspace column name
- `dtype`: logical dtype label
- `description`: human readable explanation

Optional source field:
- `raw_name`: original source header (when applicable)

Display and publication fields (recommended):
- `label`: short human-readable display label for plots/tables. This must not
  include a unit; units are formatted separately from the unit fields.
- `labels`: optional language map for `label` (`{<bcp47_tag>: <label>}`).
  Exporters may pick a target language and fall back to `label` or `name`.
- `symbol`: optional variable symbol identifier for math contexts (for example
  `h`, `d`, `u`). This must not include LaTeX math delimiters (`$...$`).
- `symbol_latex`: optional LaTeX representation of the variable symbol (without
  `$...$`). Use only when `symbol` is insufficient for publication output.
- `tags`: optional stable grouping/classification tokens (for example
  `["sensor_position"]`). Tags are not required for unit propagation and must
  not be used as join keys.

Unit fields:
- `unit`: canonical unit identifier string. When present, ArboLab treats this as
  a UCUM string.
- `unit_symbol`: optional display symbol (for example `°` or `m/s²`).
- `unit_siunitx`: optional LaTeX siunitx representation (for example
  `\meter\per\second`).
- `unit_name`: optional human-readable unit name.
- `unit_definition`: optional unit definition reference (URI or free text).

If a unit is unknown or cannot be represented in UCUM, `unit` may still be set
to a stable project-specific identifier; exporters should treat it as a fallback
label.

## Persistence Rules
### DataVariant datasets
- A `DataVariant` must persist `column_specs` that fully describe all dataset
  columns, including unit metadata.
- Persisted datasets should include a JSON documentation sidecar `dataset.json`
  alongside the dataset files for portability.

### Derived datasets
- Any persisted derived table must persist `column_specs` for every output
  column.
- Derived columns must define units explicitly. If a derived column is
  dimensionless, set `unit` to `1` (UCUM) and document the meaning via
  `description`.
- Persisted derived datasets should include a `dataset.json` sidecar next to
  the output files.

## Derivation Rules (Unit Propagation)
When transforming datasets:
- if a column is copied/renamed, keep its unit and display metadata unchanged,
- if a column is scaled (for example degrees to radians), update `unit` and all
  display fields accordingly,
- if multiple columns are combined (for example vector magnitude), define the
  resulting unit and document the derivation in the column description and/or
  dataset metadata.

## Export Expectations
Exporters (plots, LaTeX tables, CSV/Parquet exports) must obtain unit and
display metadata from ColumnSpec rather than hardcoding axis labels.

When selecting a display label:
- prefer `labels[<lang>]` (when a target language is configured),
- fall back to `label`, then `name`.

When a LaTeX export is produced:
- prefer `unit_siunitx` for unit display using `\si{...}`,
- fall back to `unit_symbol`, then `unit`.
- variable symbols are optional; if present, prefer `symbol_latex` (rendered in
  math mode by the exporter) and fall back to `symbol`.

When a plot is produced:
- prefer `unit_symbol`, then `unit`.
Variable symbols are optional and must not be conflated with `unit_symbol`.
