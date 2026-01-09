# Ubiquitous Language (Glossary)

**This glossary is the single source of truth for domain terminology.** Specifications and implementations (e.g., persistence mappings) must reference these definitions and must not redefine or overload terms.

---

## Domain Perspectives
We distinguish between four conceptual lenses:
1. **Physical / Real-World:** Identity-stable, long-lived entities (Trees, Sensors).
2. **Experimental / Campaign:** Time-bounded structures (Experiments, Runs, Deployments).
3. **Analytical / Statistical:** Units of inference and conditions (Treatments, Units).
4. **Data / Observation:** Storage-centric entities (Datastreams, Variants, Parquet).

---

## Domain Boundary
This glossary separates scientific domain entities from system/technology concepts:
- **Domain Entities:** Scientific concepts that define the problem space and are part of the domain model. In this glossary, the domain entity range is `Project` through `Location`, inclusive.
- **System / Technology Terms:** Runtime, configuration, lifecycle, or access-control concepts that exist to operate the system and are not part of the scientific domain model.

---

## Glossary

### Lab
- **Category:** System / Technology
- **Perspective:** Runtime / System Context
- **Definition:** The configured environment binding storage roots, configuration, and plugins. Provides the execution context.
- **Notes:** Not a scientific entity. It owns the `input_root`, `workspace_root`, and `results_root`.

### Project
- **Category:** Domain Entity
- **Perspective:** Experimental / Campaign
- **Definition:** A long-lived research context grouping experiments, things, and treatments under a shared scientific objective.
- **Notes:** Entities like `Tree` or `Treatment` are reusable across multiple experiments within a Project.

### Experiment
- **Category:** Domain Entity
- **Perspective:** Experimental / Campaign
- **Definition:** A time-bounded campaign within a Project, representing a coherent measurement series.
- **Notes:** Defines the temporal window for a group of Runs.

### Run
- **Category:** Domain Entity
- **Perspective:** Experimental / Campaign
- **Definition:** A concrete execution interval within an Experiment (e.g., a specific pull-test).
- **Notes:** Does **not** imply perfect temporal synchrony. Clocks may drift. Runs optionally group `SensorDeployment` records for analysis, and `SensorDeployment` records may exist without a Run.

### Thing (Tree, Cable)
- **Category:** Domain Entity
- **Perspective:** Physical / Real-World
- **Definition:** A persistent real-world object that exists independently of experiments.
- **Notes:** Can host sensors or treatments. `Tree` and `Cable` are common specializations.

### Treatment & TreatmentApplication
- **Category:** Domain Entity
- **Perspective:** Analytical (Treatment) / Experimental (Application)
- **Definition:** `Treatment` is the abstract condition (e.g., "heavy pruning"). `TreatmentApplication` is the concrete, time-bounded event of applying it to a `Thing`.

### ExperimentalUnit
- **Category:** Domain Entity
- **Perspective:** Analytical / Statistical
- **Definition:** The object of statistical inference (the "subject") within a Run.
- **Notes:** Defines *what is compared*. May reference one or more `Things` (e.g., a tree-cable system).

### SensorModel & Sensor
- **Category:** Domain Entity
- **Perspective:** Physical / Real-World
- **Definition:** `SensorModel` describes the type/capabilities (e.g., Inclinometer X). `Sensor` is the specific physical device instance.

### SensorDeployment
- **Category:** Domain Entity
- **Perspective:** Experimental / Campaign
- **Definition:** A time-bounded record of a `Sensor` installed on a `Thing` for an `ExperimentalUnit`.
- **Notes:** Captures mounting height, orientation, and calibration. **Moving a sensor = new Deployment.** May optionally belong to a `Run`.

### Datastream
- **Category:** Domain Entity
- **Perspective:** Data / Observation
- **Definition:** A logical container for a time-ordered sequence of observations from exactly **one** `SensorDeployment`.
- **Notes:** Does not aggregate data from multiple deployments.

### DatastreamChannel
- **Category:** Domain Entity
- **Perspective:** Data / Observation
- **Definition:** A single measurement channel (e.g., "Axis X") binding an `ObservedProperty` and `UnitOfMeasurement`.
- **Notes:** Smallest semantic unit. Order and meaning are fixed within a `Datastream`.

### DataVariant
- **Category:** Domain Entity
- **Perspective:** Data / Observation
- **Definition:** Metadata describing an immutable persisted version of a `Datastream` (e.g., `raw` or `filtered`).
- **Notes:** Append-only. Reprocessing results in a new `DataVariant`.

### Observation
- **Category:** Domain Entity
- **Perspective:** Data / Observation
- **Definition:** A single time-stamped measurement record within a `DataVariant`.
- **Notes:** Analyzed in bulk via DuckDB/Parquet; no canonical row-wise relational table.

### Location
- **Category:** Domain Entity
- **Perspective:** Physical / Real-World
- **Definition:** Current spatial description associated with a `Thing`.

### Workspace
- **Category:** System / Technology
- **Perspective:** Runtime / System Context
- **Definition:** A persisted configuration and storage layout bound to `input_root`, `workspace_root`, and `results_root`.
- **Notes:** Created and opened by the `Lab`. The Web App provisions Workspaces for users.

### Recipe
- **Category:** System / Technology
- **Perspective:** Runtime / Reproducibility
- **Definition:** A declarative JSON description of ingest and analysis steps executed against a Workspace.
- **Notes:** The Web App requires a Recipe for execution; direct Python usage may run without one.

### RecipeStep
- **Category:** System / Technology
- **Perspective:** Runtime / Reproducibility
- **Definition:** A single typed step inside a Recipe with a parameter payload.
- **Notes:** The executor maps step types to Lab operations.

### User
- **Category:** System / Technology
- **Perspective:** SaaS / Access Control
- **Definition:** An authenticated actor in the Web App.
- **Notes:** Stored in the SaaS metadata store and not part of the workspace domain model.

### Tenant
- **Category:** System / Technology
- **Perspective:** SaaS / Access Control
- **Definition:** A logical boundary grouping Users and Workspaces in the Web App.
- **Notes:** The MVP may operate in single-tenant mode.
