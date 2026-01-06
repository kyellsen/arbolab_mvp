# Architecture Overview

## Purpose
This document maps the ArboLab architecture documents and summarizes how the monorepo is organized.
For documentation boundaries and conventions, see `docs/README.md`.

## Repository Map
ArboLab is a monorepo with:
- Core package: `arbolab` (domain models, configuration, managers, persistence, plugin runtime, `Lab` API).
- Device packages: `arbolab-<device>` (device-specific implementations under `arbolab_plugins.*`).
- Infrastructure packages: `arbolab-logger`, `arbolab-plot-service`, `arbolab-latex-service`.

All packages use the `src/` layout under `packages/`.

## Package Conventions (Brief)
- Core code is organized by responsibility (`db/`, `models/`, `plugins/`, `schemas/`, `services/`).
- Device plugin code lives under `src/arbolab_plugins/<device>/`.

## Architecture Reading Map
- `docs/architecture/storage-format.md` for storage roots, workspace layout, and data variants.
- `docs/architecture/plugin-architecture.md` for core/plugin boundaries and discovery.
- `docs/architecture/services-manager.md` for configuration, managers, and service wiring.
- `docs/architecture/examples.md` for examples layout and fixture conventions.

## Entry Point
`Lab` is the integration point for configuration, storage, services, and plugin lifecycle. API constraints are defined in `docs/specs/core-api.md`.
