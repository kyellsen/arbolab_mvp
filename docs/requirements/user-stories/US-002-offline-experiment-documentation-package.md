# US-002: Generate and import an offline experiment documentation package

- ID: US-002
- Title: Generate and import an offline experiment documentation package
- Persona: researcher-student
- Phase: mvp

## Story
As a researcher/student planning a field or lab experiment
I want ArboLab to generate an offline documentation template as a Frictionless Tabular Data Package (`metadata/datapackage.json` + CSV resources) that I can fill with any tool, and import it back into my Lab
So that my experiment metadata becomes consistent, reproducible, and can be mapped into the ArboLab domain model without manual rework

## Notes / open questions
- No mobile app is required; the offline package is the interface.
- Legacy sources (spreadsheets, ad-hoc CSVs) should be convertible into this package.
- The template generator should scaffold the experiment input directory layout under the templates root (`results_root/templates`) so users can fill `metadata/` before copying the package into `input_root`.
- The experiment input directory under `input_root` is input-only and treated as read-only by ArboLab; generated templates and exports must never be written there directly.

## Example scenarios (Given/When/Then)
```text
Scenario: Create a new template package
  Given a Lab and a project identifier
  When I generate a documentation template under the templates root (`results_root/templates`)
  Then ArboLab creates an experiment input directory under `results_root/templates` with a versioned `datapackage.json` and empty CSV resources under `metadata/`

Scenario: Import a filled package
  Given a filled documentation package
  When I import it into ArboLab
  Then ArboLab validates IDs and references and creates the corresponding domain records

Scenario: Import fails with validation errors
  Given a package with missing required fields or broken references
  When I import it into ArboLab
  Then ArboLab produces a human-readable validation report and does not create partial inconsistent state
```

## References
- `docs/specs/metadata-package.md`
