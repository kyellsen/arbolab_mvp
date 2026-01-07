# Architecture Overview

## Purpose
This document maps the ArboLab architecture documents and summarizes how the monorepo is organized.
For documentation boundaries and conventions, see `docs/AGENTS.md`.

This file is the single source of truth for navigation within `docs/architecture/` (what lives where, and how architecture relates to requirements and specs).

## Scope
Architecture documents describe system structure, boundaries, and responsibilities (core vs plugins, services, storage layout).
Concrete, testable contracts live in `docs/specs/` (see `docs/specs/AGENTS.md`); problem-space goals live in `docs/requirements/` (see `docs/requirements/AGENTS.md`).

## Repository Map
ArboLab is a monorepo with:
- Core package: `arbolab` (domain models, configuration, managers, persistence, plugin runtime, `Lab` API).
- Device packages: `arbolab-<device>` (device-specific implementations under `arbolab_plugins.*`).
- Infrastructure packages: `arbolab-logger`, `arbolab-plot-service`, `arbolab-latex-service`.

All packages use the `src/` layout under `packages/`.

## Package Conventions (Brief)
- Core code is organized by responsibility (`managers/`, `models/`, `plugins/`, `schemas/`, `services/`).
- Device plugin code lives under `src/arbolab_plugins/<device>/`.
- Device plugin code is organized by responsibility (`managers/`, `models/`, `io/`, `schemas/`, `services/`).

## Architecture Reading Map
- `docs/architecture/storage-format.md` for storage roots, workspace layout, and data variants.
- `docs/architecture/plugin-architecture.md` for core/plugin boundaries and discovery.
- `docs/architecture/services-manager.md` for configuration, managers, and service wiring.
- `docs/architecture/examples.md` for examples layout and fixture conventions.

## Entry Point
`Lab` is the integration point for configuration, storage, services, and plugin lifecycle. API constraints are defined in `docs/specs/api.md`.
