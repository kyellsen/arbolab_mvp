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

## Glossary

### Lab
- **Perspective:** Runtime / System Context
- **Definition:** The configured environment binding storage roots, configuration, and plugins. Provides the execution context.
- **Notes:** Not a scientific entity. It owns the `input_root`, `workspace_root`, and `results_root`.

### Project
- **Perspective:** Experimental / Campaign
- **Definition:** A long-lived research context grouping experiments, things, and treatments under a shared scientific objective.
- **Notes:** Entities like `Tree` or `Treatment` are reusable across multiple experiments within a Project.

### Experiment
- **Perspective:** Experimental / Campaign
- **Definition:** A time-bounded campaign within a Project, representing a coherent measurement series.
- **Notes:** Defines the temporal window for a group of Runs.

### Run
- **Perspective:** Experimental / Campaign
- **Definition:** A concrete execution interval within an Experiment (e.g., a specific pull-test).
- **Notes:** Does **not** imply perfect temporal synchrony. Clocks may drift. For long-term monitoring, segment data into manageable Runs (e.g., monthly).

### Thing (Tree, Cable)
- **Perspective:** Physical / Real-World
- **Definition:** A persistent real-world object that exists independently of experiments.
- **Notes:** Can host sensors or treatments. `Tree` and `Cable` are common specializations.

### Treatment & TreatmentApplication
- **Perspective:** Analytical (Treatment) / Experimental (Application)
- **Definition:** `Treatment` is the abstract condition (e.g., "heavy pruning"). `TreatmentApplication` is the concrete, time-bounded event of applying it to a `Thing`.

### ExperimentalUnit
- **Perspective:** Analytical / Statistical
- **Definition:** The object of statistical inference (the "subject") within a Run.
- **Notes:** Defines *what is compared*. May reference one or more `Things` (e.g., a tree-cable system).

### SensorModel & Sensor
- **Perspective:** Physical / Real-World
- **Definition:** `SensorModel` describes the type/capabilities (e.g., Inclinometer X). `Sensor` is the specific physical device instance.

### SensorDeployment
- **Perspective:** Experimental / Campaign
- **Definition:** A time-bounded record of a `Sensor` installed on a `Thing` for an `ExperimentalUnit`.
- **Notes:** Captures mounting height, orientation, and calibration. **Moving a sensor = new Deployment.**

### Datastream
- **Perspective:** Data / Observation
- **Definition:** A logical container for a time-ordered sequence of observations from exactly **one** `SensorDeployment`.
- **Notes:** Does not aggregate data from multiple deployments.

### DatastreamChannel
- **Perspective:** Data / Observation
- **Definition:** A single measurement channel (e.g., "Axis X") binding an `ObservedProperty` and `UnitOfMeasurement`.
- **Notes:** Smallest semantic unit. Order and meaning are fixed within a `Datastream`.

### DataVariant
- **Perspective:** Data / Observation
- **Definition:** Metadata describing an immutable persisted version of a `Datastream` (e.g., `raw` or `filtered`).
- **Notes:** Append-only. Reprocessing results in a new `DataVariant`.

### Observation
- **Perspective:** Data / Observation
- **Definition:** A single time-stamped measurement record within a `DataVariant`.
- **Notes:** Analyzed in bulk via DuckDB/Parquet; no canonical row-wise relational table.

### Location
- **Perspective:** Physical / Real-World
- **Definition:** Current spatial description associated with a `Thing`.