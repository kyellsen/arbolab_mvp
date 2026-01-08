# AGENTS.md

## Purpose

This file defines **all binding rules, boundaries, and expectations** for humans, agents, and automation working in the ArboLab repository.

It is the **single and only AGENTS.md** in the project. There are **no nested or package‑local AGENTS.md files**. All scope, responsibilities, and constraints must be derived from this document and the linked normative documentation.

This file governs **how work is done** (process, discipline, constraints), **not** product requirements or architecture details.

---

## ArboLab – One‑Sentence Orientation

ArboLab is an **analytics‑first, domain‑first Python ecosystem** for reproducible analysis of experimental and field sensor data, with Parquet/DuckDB at the core.

---

## Single Source of Truth (Normative Documentation)

All product meaning lives **only** in the documentation tree below. Nothing normative may be duplicated elsewhere.

* **Requirements (problem space)** → `docs/requirements/`
* **Architecture (solution structure)** → `docs/architecture/`
* **Specifications (contracts & constraints)** → `docs/specs/`

Entry point for the documentation system:

* `docs/AGENTS.md`

---

## What This Repository Explicitly Does NOT Maintain

To keep complexity low and authority clear, ArboLab intentionally does **not** maintain:

* ADRs or decision records
* Formal Definition‑of‑Done documents
* Process manuals outside `AGENTS.md`
* Duplicated summaries of requirements, architecture, or specs

Lightweight artifacts (user stories, example scenarios, diagrams) are allowed **only** in their canonical locations.

---

## Non‑Negotiable Rules for Agents and Automation

### 1. Specs Are Law

Before implementing, refactoring, or extending anything that touches domain models, metadata, ingestion, analytics, persistence, or exports, agents **must read and follow** the following canonical specifications:

* `docs/specs/data-model.md` (domain & persistence model)
* `docs/specs/api.md` (Lab API, workspace lifecycle, layouts, stores)
* `docs/specs/plugin-requirements.md` (plugin boundaries and isolation)

If behavior is not specified there, it must not be implemented.

---

### 2. Analytics‑First Discipline

The following principles are invariant:

* Observations are **Parquet‑first**.
* Analytics operate in **DuckDB at full resolution**.
* Metadata and domain entities are **relational** (DuckDB by default).
* File‑based exports are **interoperability layers**, never core constraints.

No row‑wise canonical observation tables. SaaS concerns must be isolated in the Web App layer.

---

### 3. Domain & Entity Discipline

* Domain language is defined exclusively in `docs/requirements/glossary.md`.
* **Glossary terms are binding for naming** of variables, classes, database tables, and columns.
* Core entities must already contain the attributes needed for later STA-style facades.
* Anything not structurally required belongs in extensible properties.
* No speculative entities. No convenience shortcuts.

Model evolution must preserve reproducibility.

---

### 4. Language Policy

* **Repository content** (code, docs, comments, commits, configs): **English only**.
* **Chat output by agents** (human explanations only): **German only**.
* Chat output is never committed.

---

### 5. Filesystem & Persistence Rules

* `input_root` is strictly **read‑only**.
* All internal writes go through managed layouts under `workspace_root`.
* Results are written **only** via result writers under `results_root`.
* Absolute paths or unmanaged directories must never be persisted.

---

### 6. Plugins and Package Boundaries

* Device- or sensor-specific logic lives **only** in plugin packages.

* The core defines abstractions, registries, and lifecycle — never device code.

* Plugins may only write via provided stores and writers.

* Core ↔ plugin boundaries are defined in `docs/specs/plugin-requirements.md`.

* Package-specific scope, API surfaces, responsibilities, and limitations must be documented in the package `README.md` or `pyproject.toml`.

* No additional `AGENTS.md` files are allowed anywhere in the repository.

---

### 7. Language and Communication

#### Language Policy

* **Repository content** (code, docs, comments, commits, configs): **English only**.
* **Chat output by agents** (human explanations only): **German only**.
* Chat output is never committed.

---

### 8. Tooling and Quality Gates (Externalized)

Tooling, quality gates, and development environment contracts are defined in:

* `docs/specs/development_stack.md`

These rules are **binding** and must be followed. AGENTS.md does not duplicate tooling details.

---

## How to Change the System (Iterative MVP Mode)

This project follows an **iterative, responsibility-driven workflow** suitable for MVP and lab-phase development.

1. **Check Intent**

   * Verify terminology and intent against `docs/requirements/glossary.md`.
   * Do not invent new domain terms.

2. **Implement & Adjust**

   * Implement the code (skeleton or prototype is acceptable).
   * If implementation reveals gaps or inaccuracies in `docs/specs/`, update the spec immediately to match reality.

3. **Verify**

   * Run quality gates: tests, typing, and linting.

4. **Lock In**

   * The commit must contain both working code **and** the updated specification.

Velocity is preferred over ceremony, as long as documentation stays in sync.

---

## Commit Messages

* Commit messages must be **semantic, imperative, and in English**.
* Format: `<type>(<scope>): <summary>`

  * Examples: `feat(core): flatten measurement model, update specs`, `fix(ingest): validate units on import`.

## Development Status

ArboLab is in an **architecture‑first phase**.

* Documentation describes the **target system**.
* Implementations may lag intentionally.
* Agents must verify existence before adding new code.

---

## If You Are Unsure

If something is unclear or missing, you are authorized to infer a reasonable technical solution consistent with existing patterns (especially in `docs/architecture/`).

You **must** update the corresponding specification in the same step/PR so that code and specs evolve synchronously.

Do not invent new domain terms.

---

**This file is the only operational authority for agents in this repository.**
