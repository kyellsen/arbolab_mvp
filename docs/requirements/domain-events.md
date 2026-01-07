# Domain Events (Event Storming Lite)

## Purpose
Use a list of domain events as a lightweight backbone for requirements and
modeling. Events help clarify what happens, when it is considered "done", and
what data is relevant.

## Event Template
- Event name:
- Trigger:
- Source of truth:
- Minimal payload:
- "Done" condition (when is the event true?):
- Follow-up actions (optional):
- Notes / open questions:

## Event List (Draft)

### LabWorkspaceOpened
- Event name: LabWorkspaceOpened
- Trigger: user opens/creates a Lab workspace
- Source of truth: workspace config + workspace database
- Minimal payload: workspace roots, config version, enabled plugins
- "Done" condition (when is the event true?): the workspace configuration is persisted and the workspace database is reachable
- Notes / open questions:
  - Opening must be idempotent for an existing workspace.

### DocumentationTemplateGenerated
- Event name: DocumentationTemplateGenerated
- Trigger: user requests an offline documentation template for an experiment
- Source of truth: templates written under `results_root/templates`
- Minimal payload: project ID, template version, generated file paths
- "Done" condition (when is the event true?): the template package exists and is structurally valid (`datapackage.json` + empty CSV resources)

### MetadataPackageImported
- Event name: MetadataPackageImported
- Trigger: user imports a filled metadata package under `input_root/<experiment-input>/metadata`
- Source of truth: workspace database records (domain + measurement metadata)
- Minimal payload: import report (created/updated/unchanged), validation summary
- "Done" condition (when is the event true?): all records are validated and persisted without broken references
- Follow-up actions (optional):
  - enable file linking and ingestion for enabled plugins

### RawFilesLinked
- Event name: RawFilesLinked
- Trigger: user runs file linking for a sensor type/plugin
- Source of truth: workspace database linkage records (or validated linkage report)
- Minimal payload: run IDs, sensor IDs, raw file paths, linkage diagnostics
- "Done" condition (when is the event true?): every required file reference is resolved unambiguously, or the action fails with diagnostics and no partial inconsistent state

### DataVariantIngested
- Event name: DataVariantIngested
- Trigger: user ingests linked raw files into workspace variants
- Source of truth: Parquet datasets under `workspace_root/storage/variants/` + DataVariant metadata in the workspace database
- Minimal payload: variant IDs, stream IDs, row/column counts, time range
- "Done" condition (when is the event true?): Parquet files are written inside the workspace and the corresponding metadata record is persisted

