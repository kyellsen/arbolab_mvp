# US-004: Import an experiment metadata package into the Lab database

- ID: US-004
- Title: Import an experiment metadata package into the Lab database
- Persona: researcher-student
- Phase: mvp

## Story
As a researcher/student with a filled experiment input directory under `input_root` (including `metadata/`)
I want ArboLab to import the experiment metadata package into the Lab database with validation
So that my project and experiment structure is queryable and can later be linked to raw sensor data imports

## Notes / open questions
- The experiment input directory under `input_root` is treated as input-only and read-only.
- This import step focuses on metadata; raw time-series data ingestion is handled separately.
- The import should create or update the domain entities: Project, Experiment, Treatment, ExperimentalUnit, TreatmentApplication, Run, SensorDeployment.
- The import should also create or update the measurement metadata entities required to interpret and link sensor data (Things, Locations, TreeSpecies, Sensors, SensorModels, ObservedProperties, UnitsOfMeasurement, Datastreams, DatastreamChannels).
- Re-importing the same package should be idempotent (no duplicates; updates are applied when safe).

## Example scenarios (Given/When/Then)
```text
Scenario: Import a metadata package into an empty Lab database
  Given a Lab and a valid experiment input directory under `input_root` with a filled metadata package
  When I import the experiment metadata
  Then ArboLab creates the corresponding project, experiments, and related domain entities in the Lab database

Scenario: Re-import the same metadata package
  Given a Lab where the same metadata package was imported before
  When I import it again
  Then ArboLab does not create duplicates and reports which records were created, updated, or unchanged

Scenario: Import fails with broken references
  Given a metadata package with missing required fields or broken references between tables
  When I import it
  Then ArboLab produces a human-readable validation report and does not create partial inconsistent state
```

## References
- `docs/specs/data-model.md`
- `docs/specs/data-model-diagram.md`
