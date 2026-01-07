# US-001: Create or open a Lab

- ID: US-001
- Title: Create or open a Lab
- Persona: researcher-student
- Phase: mvp

## Story
As a researcher/student working in a notebook or Python pipeline
I want to create or open a Lab that prepares all required roots, configuration, and internal services
So that I have a consistent working environment where I can import experiment inputs, process data, and produce results reproducibly

## Notes / open questions
- The Lab defines separate roots for input (`input_root`), internal state (`workspace_root`), and results (`results_root`).
- The experiment input directory (raw import directory) should be placed under the Lab input root (`input_root`).

## Example scenarios (Given/When/Then)
```text
Scenario: Create a new Lab with separate roots
  Given I have chosen input, workspace, and results root locations
  When I create a Lab
  Then ArboLab writes a versioned config and prepares internal layouts, stores, and services for that Lab

Scenario: Open an existing Lab
  Given an existing Lab configuration
  When I open the Lab
  Then ArboLab loads the config and provides the same Lab API without re-initializing experiment inputs

Scenario: Use Lab in a notebook and in a pipeline
  Given a Lab
  When I use it from a notebook or a Python script
  Then the same Lab API works for interactive exploration and automated runs
```
