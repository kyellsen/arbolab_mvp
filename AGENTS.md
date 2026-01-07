# AGENTS.md

## Purpose
Operational rules for agents and automation working in the ArboLab repository.

This file is the single source of truth for global agent workflow rules (applies to the whole repository). More specific `AGENTS.md` files may exist in subdirectories; within their subtree they add constraints and conventions.

This file is NOT a source of truth for product requirements, architecture, or specifications.

## ArboLab (High-Level)
ArboLab is an analytics-first, domain-first toolkit for reproducible analysis of experimental sensor data (lab/field experiments). Key orientation and constraints are defined in `docs/specs/data-model.md` and `docs/specs/api.md`.

## Single Source of Truth (Normative Docs)
All normative project definitions live exclusively in:

- `docs/requirements/`  (problem space: domain goals, scope, ubiquitous language, capabilities)
- `docs/architecture/`  (solution space: system structure, boundaries, responsibilities)
- `docs/specs/`         (solution space: concrete, testable contracts and constraints)

Entry point for the documentation map: `docs/AGENTS.md`.

Normative docs must not be duplicated or restated outside their canonical location; prefer links.

## What We Do NOT Maintain
This repository does NOT maintain:
- ADRs / decision records (no rationale / alternatives / consequence write-ups)
- formal Definition-of-Done (DoD) document.

Lightweight requirement artifacts such as user stories and example-style acceptance scenarios
(for example Given/When/Then) are allowed when they clarify expected behavior.

---

## Rules for Agents and Automation

### Non-Negotiable: Follow the Specs
Before implementing or refactoring anything that touches domain models, observations, analytics, ingestion, or exports, read:
- `docs/specs/data-model.md`
- `docs/specs/api.md`
- `docs/specs/nonfunctional.md`

### Entity Discipline (Keep Complexity Low)
Follow the entity discipline described in `docs/specs/data-model.md` and `docs/requirements/glossary.md`.

### Language Policy
- Repository content language policy is defined in `docs/specs/nonfunctional.md`.
- Repository content (code, docs, comments, commits, configs) must be English.
- Chat output produced by agents MUST be German.
  (Human-facing explanations only; never committed files.)

### Package-local AGENTS
Each package under `packages/` MUST provide its own `AGENTS.md` describing
package-specific scope and constraints.

It must link back to the root policies instead of duplicating them and should
include at least:
1. Purpose and scope.
2. API surface for public classes, functions, and pydantic models.
3. Responsibilities (managers/services consumed, models introduced or extended, ingestion or reporting contributions).
4. Limitations and forbidden areas, with links to the canonical specs (for example `docs/specs/api.md` and `docs/specs/plugin-requirements.md`).
5. Testing structure and root configuration for tests.
6. Versioning and migrations.
