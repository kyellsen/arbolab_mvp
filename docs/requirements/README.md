# Requirements Overview (Vision & Scope)

## Purpose
Capture the problem-space requirements from a domain/user perspective without implementation details.
This is the entry point for requirements.

## Reading Map
- `docs/requirements/glossary.md` (terms, definitions, example sentences)
- `docs/requirements/user-stories/` (user stories with example scenarios)
- `docs/requirements/domain-events.md` (event list used as a modeling backbone)

## Personas and Usage Modes
ArboLab is designed for three primary usage modes. The product will be built in phases; the modes below are used to guide scope and prioritization.

### Persona 1 (Primary): Researcher / Student (Notebook & Pipeline)
- Profile: scientific user with statistics and domain expertise.
- Goal: explore, process, and analyze tree sensor data with maximal flexibility.
- Typical interaction: Jupyter notebooks and custom data-science pipelines.
- Needs: composable APIs, reproducibility, inspectable intermediate results, and the ability to extend workflows.

### Persona 2 (Secondary): Tree Safety Expert (Standard Workflows)
- Profile: practitioner focused on standardized assessments (for example pulling tests / load tests, acoustic tomography).
- Goal: run established analysis workflows and obtain interpretable results (stability / fracture safety indicators) with minimal customization.
- Typical interaction: notebook-based workflows composed of predefined analysis blocks.
- Needs: guided workflows, sane defaults, and clear outputs; limited need for experimental exploration.

### Persona 3 (Future): SaaS Backend (Web Frontend Integration)
- Profile: ArboLab used as a backend behind a web UI for Persona 2-like workflows.
- Goal: execute workflows as services (potentially at scale) and expose results to a UI.
- Typical interaction: service/API integration (no notebooks required).
- Needs: stable boundaries, replaceable components, and a path to job-style execution; not a near-term feature target.

### Phasing
- MVP focus: Persona 1.
- Next: Persona 2 built on Persona 1 capabilities.
- Later: Persona 3 constraints considered to avoid architectural dead-ends, but features are deferred.

## Vision
- TBD (what outcomes should exist if ArboLab succeeds?)

## Problem Statement
- TBD (what is hard today, for whom, and why?)

## Target Users / Roles
- TBD

## Top Use Cases (List)
- TBD

## Goals
- TBD

## Non-Goals
- TBD

## Scope
- In scope: TBD
- Out of scope: TBD

## Success Signals (Informal)
- TBD (avoid formal DoD; describe what "good" looks like)

## Constraints / Risks (High Level)
- TBD

## Notes
Concrete, testable contracts and nonfunctional/process constraints live in `docs/specs/`.

## Conventions (Input Data Package)
ArboLab operates on an input-only, read-only experiment input directory provided by the user (raw import directory) under `input_root`.
It should contain:
- `metadata/`: the experiment documentation package (manifest + CSV/JSON tables)
- one subdirectory per sensor/source type (for example `ls3/`, `tms/`) containing raw sensor exports in their native formats

The raw import directory is typically placed under the Lab input root (`input_root`).

Example layout:

```text
<experiment-input>/
  metadata/
    manifest.json (or .yaml)
    *.csv / *.json
  ls3/
    ...
  tms/
    ...
```

The documentation template generator should scaffold this structure under the templates root (`results_root/templates`) so users can fill `metadata/` in the field and later place sensor exports alongside it on their PC.
Template generation and metadata package exports must never write to `input_root`; they can be copied into `input_root` by the user when ready.
