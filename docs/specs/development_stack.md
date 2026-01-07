# Development Stack and Quality Gates

**Binding Rules**: See `../../AGENTS.md`.

This document defines the **binding technical development contract** for the ArboLab repository.

It specifies the toolchain, environment expectations, and quality gates that all contributors and agents must follow.

This file is normative. If code changes require adjustments here, this file must be updated in the same commit.

---

## Language and Code Standards

* Repository content (code, docs, comments, commits, configs) must be **English**.
* Chat output produced by agents (human-facing explanations only) must be **German** and is never committed.
* Python version is **>= 3.12**.

Every module, class, function, and method must:

* provide explicit type hints,
* include a Google-style docstring describing purpose, key parameters, and return values (where applicable).

Persisted metadata and configuration models:

* must use **Pydantic v2**,
* should be declared with `frozen=True` unless mutation is explicitly required.

In-memory dataset containers may use `dataclasses`.

---

## Tooling and Environment

* Each package defines metadata and dependencies in its own `pyproject.toml`.
* Dependency and environment management uses **uv**.

Canonical workflow:

* Create and activate a virtual environment: `uv venv`
* Install dependencies: `uv sync`

Linting and formatting use **ruff**.

---

## Linting, Typing, and Tests

The following checks must pass before every commit:

* `uv run ruff check --fix packages/`
* `uv run mypy packages/`
* `uv run pytest`

The root `pyproject.toml` configures the workspace so that `ruff`, `mypy`, and `pytest` see all package `src/` trees.

---

## Setup Script Contract

`setup.sh` is the canonical bootstrap entry point and must:

* verify that `uv` is installed,
* create or recreate `.venv`,
* run `uv sync`,
* print the canonical commands for tests, linting, and typing.

---

## CI and Automation Expectations

* CI pipelines must enforce the same quality gates as local development.
* CI must not introduce additional hidden rules beyond those defined here.
* Tooling changes must be reflected in this document.

---

This file, together with `../../AGENTS.md`, defines the complete operational and technical contract for working in the ArboLab repository.
