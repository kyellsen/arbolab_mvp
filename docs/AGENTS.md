# Documentation Map

This directory contains the normative project documentation.

## Directory Responsibilities

### `docs/requirements/` (Problem Space)
Defines what the system must achieve from a domain perspective:
- vision, goals, and scope (including explicit out-of-scope)
- actors and capabilities
- key use cases (lightweight narratives and examples; avoid formal DoD documents)
- ubiquitous language (terms and definitions)

Keep this layer free of implementation details and nonfunctional/process constraints.

Minimal artifact set:
- `docs/requirements/AGENTS.md` (vision & scope)
- `docs/requirements/glossary.md` (glossary)
- `docs/requirements/user-stories/AGENTS.md` (stories with example scenarios)
- `docs/requirements/domain-events.md` (event list)

### `docs/architecture/` (Solution Space: Structure)
Defines how the system is structured at a high level:
- package and module boundaries (core vs plugins)
- major components and their responsibilities
- integration points and cross-cutting infrastructure

Architecture may reference specs for concrete contracts.

### `docs/specs/` (Solution Space: Contracts)
Defines concrete, testable contracts and constraints:
- public APIs and behavioral rules
- data model and storage contracts
- nonfunctional and process requirements (tooling, typing, tests)

## Project Orientation (High-Level)
ArboLab is analytics-first and domain-first:
- Observations are Parquet-first and are analysed in DuckDB at full resolution.
- Metadata and domain entities are relational (DuckDB by default).
- Standards such as SensorThings API (STA) / OData are treated as optional
  export/facade layers derived from the core, not as internal schema drivers.

## Conventions
- Each directory should expose an entry point named `AGENTS.md`.
- Use descriptive filenames in `kebab-case.md` (no numeric prefixes).
