# Metadata Import Pathways

## Purpose and Scope
Define supported pathways for bringing experiment metadata into a Lab. The
canonical target is the Lab database (ArboLab's canonical domain model).

## Supported Pathways
- Documentation package import: a Frictionless Data Package descriptor
  (`metadata/datapackage.json`) and its resources under
  `input_root/<experiment-input>/metadata` (see `docs/specs/metadata-package.md`).

## Non-Goals
- Direct mapping from ad-hoc/legacy sources into the Lab database without first
  producing a valid metadata package.

## Notes
- Legacy sources (spreadsheets, ad-hoc CSVs) MAY be converted into a metadata
  package, but the import contract is always the package interface.
- Import requirements and scenarios are captured in:
  - `docs/requirements/user-stories/US-004-import-metadata-package-into-lab-db.md`
