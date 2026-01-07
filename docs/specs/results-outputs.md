# Results and Outputs

## Purpose and Scope
This document defines how ArboLab writes plots, tables, and reports as publication-ready artifacts.

## Results Root Is Output-Only
- All publication artifacts must be written under `results_root`.
- Results artifacts must never be treated as pipeline inputs.
- Documentation templates are written under `results_root/templates`.

## Canonical Results Directories
- Callers must derive output locations through a Lab-managed results layout helper (for example `ResultsLayout`).
- Directory creation for results is owned by `ResultsWriter` (or by the optional services that use it); ad-hoc `mkdir` calls are discouraged.
- Results paths must be safe to construct from user-provided names (no path traversal; sanitised segments).
- Canonical result categories include:
  - plots
  - exports (tables and datasets)
  - latex (report exports)

## Optional Service Integrations
- Plotting and LaTeX reporting may be provided by optional packages.
- Plotting and LaTeX services are optional extras and are not required for the MVP runtime.
- Optional services must resolve output locations through `ResultsLayout` and may use `ResultsWriter` to prepare directories.
- The Lab API must expose optional accessors for these services.
  - When optional access is requested and a service is not installed, the accessor must return `None`.
  - When a service is required and not installed, the accessor must raise a clear error with installation guidance.
- When optional services are not installed, ArboLab must provide clear, actionable diagnostics instead of failing silently.
