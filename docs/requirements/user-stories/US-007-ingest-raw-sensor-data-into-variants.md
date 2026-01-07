# US-007: Ingest linked raw sensor data into workspace variants

- ID: US-007
- Title: Ingest linked raw sensor data into workspace variants
- Persona: researcher-student
- Phase: mvp

## Story
As a researcher/student with raw sensor exports placed in the Lab input root (`input_root`) and linked to metadata
I want ArboLab to ingest those raw files into standardized DataVariants stored under `workspace_root`
So that my analyses can operate on consistent, queryable datasets without modifying the original raw inputs

## Notes / open questions
- The experiment input directory under `input_root` is treated as input-only and read-only.
- Ingestion is expected to be sensor-specific and typically provided by plugins.
- Ingestion runs only for enabled plugins; disabled or missing plugins must be reported.
- Linking raw files to Runs/Sensors/SensorDeployments happens before ingestion and is defined in US-006.
- Re-running ingestion should be safe (idempotent or explicitly versioned via DataVariants).

## Example scenarios (Given/When/Then)
```text
Scenario: Ingest raw data after successful linking
  Given an experiment input directory under `input_root` with a filled metadata package, raw sensor exports, and a validated file linkage
  When I ingest raw sensor data
  Then ArboLab creates one or more DataVariants under `workspace_root` and records their metadata in the Lab database

Scenario: Re-run ingestion without creating duplicates
  Given the same experiment input directory under `input_root` and an existing Lab
  When I ingest raw sensor data again
  Then ArboLab does not create duplicate variants and reports what was created, updated, or skipped
```

## References
- `docs/specs/data-variants.md`
- `docs/architecture/storage-format.md`
- `docs/specs/data-model.md`
