# AGENTS.md

## Purpose
Operational rules for agents and automation working in the ArboLab repository.

This file is NOT a source of architectural truth.

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

### 1) Allowed Scope
Agents MAY:
- implement code consistent with `docs/requirements/`, `docs/architecture/`, and `docs/specs/`
- refactor without changing requirements/architecture/spec intent
- add tests, documentation, examples

Agents MUST NOT:
- introduce or modify requirements/architecture/specs implicitly
- deviate from defined core/plugin boundaries

### 2) Changes to Requirements, Architecture, or Specs
If normative docs are missing/outdated/conflicting, the agent MUST:
1. stop implementation,
2. propose updates to `docs/requirements/`, `docs/architecture/`, and/or `docs/specs/`,
3. wait for approval.

No normative change without updating docs.

### 3) Language Policy
- Repository content MUST be English (code, docs, comments, commits, configs).
- Chat output produced by agents MUST be German.
  (Human-facing explanations only; never committed files.)
