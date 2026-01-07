# AGENTS.md

## Purpose
Operational rules for agents and automation working in the ArboLab repository.

This file is NOT a source of truth for requirements, architecture and specs. It describes general guardrails for Agents.

---

## Single Source of Truth
All normative project definitions live exclusively in:

- `docs/requirements/`  (domain goals, scope, ubiquitous language, capabilities)
- `docs/architecture/`  (system structure, boundaries, and responsibilities)
- `docs/specs/`         (concrete, testable contracts and constraints)

Normative docs MUST NOT be duplicated or restated in this file.

---

## What We Do NOT Maintain
This repository does NOT maintain:
- ADRs / decision records (no rationale / alternatives / consequence write-ups)
- formal Definition-of-Done (DoD) documents

Only requirements, architecture, and specifications are normative.

Lightweight requirement artifacts such as user stories and example-style acceptance scenarios
(for example Given/When/Then) are allowed when they clarify expected behavior.

---

## Rules for Agents and Automation

### 0) Non-Negotiable Guardrails (Analytics-First, Domain-First)
Agents MUST:
- treat the domain model as canonical and use domain language first
- treat observations as Parquet-first, queried via DuckDB
- keep interoperability/export formats (for example STA/OData) as derived
  projections, not internal schema drivers

Agents MUST NOT:
- introduce a canonical relational Observation table (observations are not
  modelled as row-based domain entities)
- introduce or evolve an internal "STA core schema" that constrains the domain
  model
- expose full-resolution observations through STA/OData; exports must be limited
  to preview/downsampled access

See:
- `docs/specs/data-model.md`
- `docs/specs/analytics-api.md`
- `docs/specs/sta-export.md`

### Allowed Scope
Agents MAY:
- implement code consistent with `docs/requirements/`, `docs/architecture/`, and `docs/specs/`
- refactor without changing requirements/architecture/spec intent
- add tests, documentation, examples

Agents MUST NOT:
- introduce or modify requirements/architecture/specs implicitly
- deviate from defined core/plugin boundaries

### Changes to Requirements, Architecture, or Specs
If normative docs are missing/outdated/conflicting, the agent MUST:
1. stop implementation,
2. propose updates to `docs/requirements/`, `docs/architecture/`, and/or `docs/specs/`,
3. wait for approval.

No normative change without updating docs.

### Entity Discipline (Keep Complexity Low)
Agents SHOULD introduce a new entity/table only when it carries responsibility
that must be addressable, validated, joined, historized, or versioned.

### Language Policy
- Repository content MUST be English (code, docs, comments, commits, configs).
- Chat output produced by agents MUST be German.
  (Human-facing explanations only; never committed files.)
