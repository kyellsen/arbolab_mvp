# Specification Overview

## Purpose
Entry point and map for the concrete, testable specifications under `docs/specs/`.

This file is the single source of truth for navigation within the specs directory (what lives where, and how specs relate to requirements and architecture).

## Scope
Specs define contracts and constraints that drive implementation.
- Problem-space goals belong in `docs/requirements/` (see `docs/requirements/AGENTS.md`).
- High-level system structure belongs in `docs/architecture/` (see `docs/architecture/AGENTS.md`).

Cross-cutting development and contribution rules are defined in:
- `AGENTS.md` (global agent workflow rules)
- `docs/specs/nonfunctional.md` (tooling, typing, testing, process)

## Specification Map
- `docs/specs/data-model.md` for the domain and persistence data model.
- `docs/specs/data-model-diagram.md` for the Mermaid ER diagram of the model.
- `docs/specs/api.md` for the `Lab` API (single entry point), workspace lifecycle, config access, managers, and domain/metadata + analytics entry points.
- `docs/specs/metadata-import.md` for supported metadata import pathways.
- `docs/specs/plugin-requirements.md` for plugin packaging, discovery, and isolation.
- `docs/specs/data-variants.md` for ingesting raw inputs into workspace datasets.
- `docs/specs/results-outputs.md` for results directory conventions and optional output services.
- `docs/specs/units-and-data-dictionary.md` for unit metadata, column specs, and dataset documentation sidecars.
- `docs/specs/nonfunctional.md` for tooling, tests, and process requirements.

## Development Stage
The project is in an architecture stage. Contributors must check whether features already exist and implement only what is explicitly requested. Most concrete implementations are intentionally missing until the architecture is finalized.
