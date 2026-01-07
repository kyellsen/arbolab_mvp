# Ubiquitous Language

## Purpose
Define domain terms so conversations, documentation, and code use the same
language and the same meanings.

This glossary is the **single source of truth** for domain terminology.
Specifications and implementations (for example persistence mappings in
`docs/specs/data-model.md`) must reference these definitions and should avoid
redefining or overloading terms.

---

## Domain Perspectives

This model distinguishes between multiple **domain perspectives**.
Each entity belongs primarily to one perspective, which defines its role,
lifecycle, and interpretation.

Perspectives are **conceptual lenses**, not technical layers.

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

### Run
- **Perspective:** Experimental / Campaign
- **Definition:** A concrete execution interval within an Experiment representing a logically coherent measurement session.
- **Synonyms / aliases (avoid in code):** session
- **Example sentences:**
  - "Run 03 contains the data collected during the pull-and-release execution."
- **Notes:**
  - A Run groups measurements that belong to the same execution context.
  - A Run does **not** imply perfect temporal synchrony between sensors.
  - Sensor clocks may start asynchronously or drift; synchronization quality is a property of the Run, not a guarantee.
  - Runs may contain internal phases (for example setup, loading, relaxation), but phase modeling is out of scope at this level.

---

### ExperimentalUnit
- **Perspective:** Analytical / Statistical
- **Definition:** A conceptual unit of analysis representing a defined object of inference within a Run.
- **Synonyms / aliases (avoid in code):** unit, subject
- **Example sentences:**
  - "Each ExperimentalUnit is analysed separately in the mixed-effects model."
- **Notes:**
  - An ExperimentalUnit defines *what is compared statistically*, not necessarily a single physical object.
  - An ExperimentalUnit typically references one Thing, but may conceptually represent a specific part, configuration, or combination thereof.
  - Treatments are associated with ExperimentalUnits via TreatmentApplications.
  - ExperimentalUnits are identity-stable within their analytical context.

---

### SensorDeployment
- **Perspective:** Experimental / Campaign
- **Definition:** A time-bounded record describing how a Sensor is installed on a Thing in the context of an ExperimentalUnit.
- **Synonyms / aliases (avoid in code):** installation, mounting
- **Example sentences:**
  - "The SensorDeployment mounts the inclinometer at 1.2 m height on Tree 12."
- **Notes:**
  - A SensorDeployment captures the *effective measurement configuration*.
  - Mounting position, orientation, channel mapping, and effective calibration parameters belong here.
  - When a sensor is reconfigured, moved, or remounted, a **new SensorDeployment** is created.

---

### Datastream
- **Perspective:** Data / Observation
- **Definition:** A logical container representing a time-ordered sequence of observations produced by exactly one SensorDeployment for an ExperimentalUnit.
- **Synonyms / aliases (avoid in code):** stream
- **Example sentences:**
  - "Each SensorDeployment produces one or more Datastreams."
- **Notes:**
  - **A Datastream originates from exactly one SensorDeployment.**
  - A Datastream does not aggregate data from multiple deployments.
  - A Datastream may contain multiple DatastreamChannels.
  - Changes in sensor configuration do **not** silently reuse an existing Datastream.

---

### DatastreamChannel
- **Perspective:** Data / Observation
- **Definition:** A single measurement channel within a Datastream, binding an ObservedProperty and a UnitOfMeasurement to individual values.
- **Synonyms / aliases (avoid in code):** channel
- **Example sentences:**
  - "The DatastreamChannel represents inclination in degrees."
- **Notes:**
  - Channel order, count, and semantic meaning are fixed for a Datastream.
  - Channels are defined based on SensorModel capabilities and SensorDeployment configuration.

---

### SensorModel
- **Perspective:** Physical / Real-World
- **Definition:** Reusable metadata describing a sensor type and its measurement capabilities.
- **Synonyms / aliases (avoid in code):** sensor type
- **Example sentences:**
  - "All inclinometers of this type share one SensorModel."
- **Notes:**
  - SensorModel defines *capabilities* (supported channels, nominal units, sampling limits).
  - SensorModel does not describe deployment-specific configuration.

---

### DataVariant
- **Perspective:** Data / Observation
- **Definition:** Metadata describing an immutable persisted variant of a Datastream (for example raw or derived).
- **Synonyms / aliases (avoid in code):** variant
- **Example sentences:**
  - "A new raw DataVariant is created during ingestion."
- **Notes:**
  - DataVariants are append-only and immutable.
  - Reprocessing or reinterpretation results in a **new DataVariant**, never in-place modification.
  - Changes in SensorDeployment configuration may result in a new DataVariant or a new Datastream, depending on scope.
