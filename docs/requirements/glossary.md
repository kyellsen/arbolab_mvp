# Ubiquitous Language

## Purpose
Define domain terms so conversations, documentation, and code use the same
language and the same meanings.

This glossary is the **single source of truth** for domain terminology.
Specifications and implementations (for example persistence mappings in
`docs/specs/data-model.md`) must reference these definitions and must not
redefine or overload terms.

---

## Domain Perspectives

This domain model distinguishes between multiple **perspectives**.
Each entity belongs primarily to one perspective, which defines its role,
lifecycle, and interpretation.

Perspectives are **conceptual lenses**, not technical layers or inheritance
hierarchies.

### Physical / Real-World Perspective
Entities that exist independently of experiments and persist over time.

**Characteristics**
- Persistent and identity-stable
- Long-lived
- Reusable across multiple experiments

---

### Experimental / Campaign Perspective
Entities that structure measurement campaigns and executions.

**Characteristics**
- Time-bounded or event-bounded
- Describe *when* and *under which conditions* measurements occur
- Bind physical entities into experimental context

---

### Analytical / Statistical Perspective
Entities constructed to support comparison, inference, and modeling.

**Characteristics**
- Often non-physical
- Central to experimental design and statistics
- Define units of analysis

---

### Data / Observation Perspective
Entities that describe data production, semantics, and storage.

**Characteristics**
- Data-driven and often high-volume
- Closely coupled to schema and storage
- Basis for computation and analysis

---

## Term Template
- Term:
- Perspective:
- Definition:
- Synonyms / aliases (avoid in code):
- Example sentences (use in conversations and docs):
- Notes:

---

## Glossary

### Lab
- **Perspective:** Runtime / System Context
- **Definition:** The configured ArboLab environment that binds storage roots, configuration, managers, and plugins, and provides the execution context for projects and experiments.
- **Synonyms / aliases (avoid in code):** environment, workspace
- **Example sentences:**
  - "Open the Lab before importing metadata."
  - "The Lab owns the input_root, workspace_root, and results_root."
- **Notes:**
  - The Lab is not a scientific domain entity.
  - It provides configuration and execution context only.

---

### Project
- **Perspective:** Experimental / Campaign
- **Definition:** A long-lived research context that groups related experiments, things, sensors, treatments, and metadata under a shared scientific objective.
- **Synonyms / aliases (avoid in code):** study, campaign
- **Example sentences:**
  - "This Project investigates dynamic loads in crown bracing systems."
  - "Multiple experiments can belong to the same Project."
- **Notes:**
  - Project-level entities are reusable across experiments.
  - A Project does not represent a single experimental execution.

---

### Experiment
- **Perspective:** Experimental / Campaign
- **Definition:** A time-bounded experimental campaign within a Project, representing a coherent measurement series that may contain one or more Runs.
- **Synonyms / aliases (avoid in code):** measurement campaign
- **Example sentences:**
  - "The Experiment ran from May to July and included five Runs."
- **Notes:**
  - An Experiment defines temporal scope.
  - Concrete simultaneity is represented by Runs.

---

### Run
- **Perspective:** Experimental / Campaign
- **Definition:** A concrete execution interval within an Experiment representing a logically coherent measurement session.
- **Synonyms / aliases (avoid in code):** session
- **Example sentences:**
  - "Run 03 contains the data collected during the pull-and-release execution."
- **Notes:**
  - A Run groups measurements belonging to the same execution context.
  - A Run does **not** imply perfect temporal synchrony between sensors.
  - Sensor clocks may start asynchronously or drift.
  - Runs may be short-lived events or long-running monitoring sessions.
  - For long-term monitoring, ArboLab recommends segmenting data into
    manageable Runs (e.g. monthly or quarterly) by convention.

---

### Thing
- **Perspective:** Physical / Real-World
- **Definition:** A persistent real-world object of interest that exists independently of experiments and can host sensors or treatments.
- **Synonyms / aliases (avoid in code):** object, asset
- **Example sentences:**
  - "Tree 12 is represented as a Thing."
- **Notes:**
  - A Thing may represent a whole object or a persistent sub-component
    (for example a branch, stem segment, or cable section), depending on
    the modeling granularity of the Project.
  - Tree and Cable are common specializations of Thing.

---

### Tree
- **Perspective:** Physical / Real-World
- **Definition:** A Thing representing a tree used as an observed or experimental object.
- **Synonyms / aliases (avoid in code):** none
- **Example sentences:**
  - "Tree 12 is reused across multiple experiments."
- **Notes:**
  - Trees are long-lived and may participate in many experiments.

---

### TreeSpecies
- **Perspective:** Physical / Real-World
- **Definition:** A reusable classification describing the species of a Tree.
- **Synonyms / aliases (avoid in code):** species
- **Example sentences:**
  - "Tree 12 is classified as TreeSpecies 'Acer pseudoplatanus'."
- **Notes:**
  - TreeSpecies may be shared across multiple projects.

---

### Cable
- **Perspective:** Physical / Real-World
- **Definition:** A Thing representing a cable system or installed cable component.
- **Synonyms / aliases (avoid in code):** none
- **Example sentences:**
  - "Cable C1 is recorded as a Cable Thing."
- **Notes:**
  - Cables may be treated as independent Things or as components of trees.

---

### Treatment
- **Perspective:** Analytical / Statistical
- **Definition:** A project-scoped, abstract definition of an experimental condition or intervention, describing one or more factor levels.
- **Synonyms / aliases (avoid in code):** condition, intervention
- **Example sentences:**
  - "Different Treatments are compared within the same Experiment."
- **Notes:**
  - Treatments are abstract and reusable.
  - Treatments are not time-bounded.
  - Treatments are instantiated exclusively via TreatmentApplications.

---

### TreatmentApplication
- **Perspective:** Experimental / Campaign
- **Definition:** A concrete, time-bounded application of a Treatment to a Thing within an experimental context.
- **Synonyms / aliases (avoid in code):** applied treatment
- **Example sentences:**
  - "TreatmentApplication A1 applies 'cobra_static' from 10:00 to 11:00."
- **Notes:**
  - Represents an actual event.
  - Multiple TreatmentApplications on the same Thing enable within-subject
    and mixed experimental designs.

---

### ExperimentalUnit
- **Perspective:** Analytical / Statistical
- **Definition:** A conceptual unit of analysis representing a defined object of statistical inference within a Run.
- **Synonyms / aliases (avoid in code):** unit, subject
- **Example sentences:**
  - "Each ExperimentalUnit is analysed separately in the mixed-effects model."
- **Notes:**
  - An ExperimentalUnit defines *what is compared statistically*.
  - It is not necessarily a single physical object.
  - An ExperimentalUnit may reference one or more Things (for example a
    group of trees, a tree–cable system, or a specific sub-component).
  - ExperimentalUnits are identity-stable within their analytical context.
  - Treatments are associated via TreatmentApplications.

---

### SensorModel
- **Perspective:** Physical / Real-World
- **Definition:** Reusable metadata describing a sensor type and its measurement capabilities.
- **Synonyms / aliases (avoid in code):** sensor type
- **Example sentences:**
  - "All inclinometers of this type share one SensorModel."
- **Notes:**
  - SensorModel defines capabilities such as supported channels,
    nominal units, and sampling limits.
  - SensorModel does not describe deployment-specific configuration.

---

### Sensor
- **Perspective:** Physical / Real-World
- **Definition:** A physical measurement device capable of producing observations according to a SensorModel.
- **Synonyms / aliases (avoid in code):** device
- **Example sentences:**
  - "Sensor 83 recorded inclination during the Run."
- **Notes:**
  - Sensors are portable and reusable across experiments.

---

### SensorDeployment
- **Perspective:** Experimental / Campaign
- **Definition:** A time-bounded record describing how a Sensor is installed on a Thing in the context of an ExperimentalUnit.
- **Synonyms / aliases (avoid in code):** installation, mounting
- **Example sentences:**
  - "The SensorDeployment mounts the inclinometer at 1.2 m height."
- **Notes:**
  - A SensorDeployment captures the effective measurement configuration.
  - Mounting position, orientation, channel mapping, and effective
    calibration parameters belong here.
  - When a sensor is moved, reconfigured, or remounted, a new
    SensorDeployment is created.

---

### Datastream
- **Perspective:** Data / Observation
- **Definition:** A logical container representing a time-ordered sequence of observations produced by exactly one SensorDeployment for an ExperimentalUnit.
- **Synonyms / aliases (avoid in code):** stream
- **Example sentences:**
  - "Each SensorDeployment produces one or more Datastreams."
- **Notes:**
  - A Datastream originates from exactly one SensorDeployment.
  - Datastreams do not aggregate data from multiple deployments.
  - Configuration changes do not silently reuse an existing Datastream.
  - A Datastream may contain multiple DatastreamChannels.

---

### DatastreamChannel
- **Perspective:** Data / Observation
- **Definition:** A single measurement channel within a Datastream, binding an ObservedProperty and a UnitOfMeasurement to individual values.
- **Synonyms / aliases (avoid in code):** channel
- **Example sentences:**
  - "The DatastreamChannel represents inclination in degrees."
- **Notes:**
  - This is the smallest semantically unambiguous measurement unit.
  - Channel order, count, and semantic meaning are fixed for a Datastream.
  - Missing values or sensor dropouts do not change channel semantics.

---

### ObservedProperty
- **Perspective:** Data / Observation
- **Definition:** The conceptual definition of what is being measured, independent of sensor, unit, or experiment.
- **Synonyms / aliases (avoid in code):** none
- **Example sentences:**
  - "Inclination is an ObservedProperty."
- **Notes:**
  - ObservedProperty defines meaning, not representation.

---

### UnitOfMeasurement
- **Perspective:** Data / Observation
- **Definition:** The unit used to represent numerical values of an ObservedProperty.
- **Synonyms / aliases (avoid in code):** unit
- **Example sentences:**
  - "Inclination is stored in degrees."
- **Notes:**
  - Units are bound at the DatastreamChannel level.

---

### DataVariant
- **Perspective:** Data / Observation
- **Definition:** Metadata describing an immutable persisted variant of a Datastream (for example raw or derived).
- **Synonyms / aliases (avoid in code):** variant
- **Example sentences:**
  - "A new raw DataVariant is created during ingestion."
- **Notes:**
  - DataVariants are append-only and immutable.
  - Reprocessing or reinterpretation results in a new DataVariant.
  - Changes in SensorDeployment configuration may result in a new
    DataVariant or a new Datastream, depending on scope.

---

### Observation
- **Perspective:** Data / Observation
- **Definition:** A single time-stamped measurement record belonging to a DataVariant.
- **Synonyms / aliases (avoid in code):** sample
- **Example sentences:**
  - "Observations are stored as Parquet rows."
- **Notes:**
  - Observations are analysed in bulk via DuckDB.
  - There is no canonical relational Observation table.

---

### Location
- **Perspective:** Physical / Real-World
- **Definition:** A current spatial description associated with a Thing.
- **Synonyms / aliases (avoid in code):** none
- **Example sentences:**
  - "The Location stores the tree’s coordinates."
- **Notes:**
  - A Thing references at most one current Location.
  - Locations may be shared across multiple Things.
  - Location history is out of scope in the canonical model.
