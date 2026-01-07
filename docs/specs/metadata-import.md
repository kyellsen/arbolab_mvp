# Metadata Import Pathways

## Purpose and Scope
Define supported pathways for bringing experiment metadata into a Lab. The
canonical target is the Lab database (ArboLab's canonical domain model).

## Supported Pathways
- Documentation package import: manifest and tables under `input_root/metadata`.
- Direct mapping: legacy sources may map directly into the Lab database schema
  without generating a documentation package.

## Direct Mapping Contract
- Direct mappers must use Lab-managed database sessions (`WorkspaceDatabase`) and the
  registered SQLAlchemy metadata collections (core + plugins).
- Direct mappers must treat the domain model as canonical and must not alter
  schema definitions.
- Direct mapping must apply the same validation, reference integrity, and
  idempotency expectations as metadata package import (see
  `docs/requirements/user-stories/US-004-import-metadata-package-into-lab-db.md`).
