# US-006: Link metadata to raw sensor files before ingestion

- ID: US-006
- Title: Link metadata to raw sensor files before ingestion
- Persona: researcher-student
- Phase: mvp

## Story
As a researcher/student with a filled experiment input directory under `input_root` (including `metadata/` and sensor folders)
I want ArboLab to link metadata entities to the corresponding raw sensor files using sensor-specific plugin logic before ingesting time-series data
So that I can validate completeness and correctness and avoid importing the wrong files

## Notes / open questions
- Linking typically relies on file paths, file names, and identifiers embedded in the raw files (for example sensor IDs).
- The linking logic is sensor-type specific and is expected to be provided by plugins.
- Linking runs only for enabled plugins; disabled or missing plugins must be reported.
- Linking must be validated (missing files, ambiguous matches, inconsistent sensor IDs).

## Example scenarios (Given/When/Then)
```text
Scenario: Link raw files for a supported sensor type
  Given an experiment input directory under `input_root` with a filled metadata package and raw files for a supported sensor type
  When I prepare ingestion by linking metadata to raw files
  Then ArboLab produces a mapping between Runs, SensorDeployments, their Datastreams, and the raw sensor files and reports a summary

Scenario: Linking fails due to missing or ambiguous files
  Given a metadata package that refers to raw files that are missing or ambiguous
  When I prepare ingestion by linking metadata to raw files
  Then ArboLab produces a human-readable validation report and does not proceed to ingestion

Scenario: Unknown or disabled sensor folder is reported
  Given an experiment input directory under `input_root` containing a sensor folder without an enabled plugin
  When I prepare ingestion by linking metadata to raw files
  Then ArboLab reports the missing plugin and suggests how to install it
```

## References
- `docs/specs/data-model.md`
- `docs/specs/data-model-diagram.md`
