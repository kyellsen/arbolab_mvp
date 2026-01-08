# ArboLab

**ArboLab is an analytics‑first, domain‑first Python ecosystem for reproducible analysis of experimental and field sensor data.**

It acts as a bridge between raw physical observations (from sensors on trees, cables, and other "Things") and high-level scientific insights. By leveraging Parquet for observation storage and DuckDB for relational metadata and analytical processing, ArboLab ensures both performance and strict domain alignment.

## 🚀 Key Concepts

- **Domain-First:** All entities (Projects, Experiments, Sensors, Trees) follow a strict, normative glossary and data model.
- **Analytics-First:** Observations are stored in Parquet (Wide Layout) and processed at full resolution via DuckDB.
- **Hybrid Storage:** 
    - **Core/Analytics:** Filesystem-based (DuckDB/Parquet) for scientific data and Lab workspaces.
    - **Web/SaaS:** PostgreSQL-based for multi-tenancy, identity, and application state.
- **Reproducibility:** Every ingestion and analysis step is trackable within a managed Lab workspace.

## 🚀 Getting Started (Zero-Config)

1. **Install Docker** (or Podman).
2. **Start the environment**:
   ```bash
   docker compose up
   ```
3. **Access the App**: [http://localhost:8000](http://localhost:8000)

See the **[Deployment Guide](./docs/deployment.md)** for more details on directory structure and persistence.

---

## 🤖 For Agents & AI

**STOP.** Read the operational constitution first:

👉 **[AGENTS.md](./AGENTS.md)**

This file contains all binding rules, context boundaries, and filesystem constraints.


## 📚 For Humans (Documentation)

The documentation is strict and normative. It is organized as follows:

- **Requirements & Domain Language:** `docs/requirements/` (Glossary, high-level needs)
- **Architecture & Design:** `docs/architecture/` (System structure, boundaries)
- **Technical Specifications:** `docs/specs/` (Data models, APIs, plugins)

## Development Status

ArboLab is currently in an **architecture‑first phase**. The documentation describes the target system, and implementation follows an iterative MVP approach.

## License

MIT