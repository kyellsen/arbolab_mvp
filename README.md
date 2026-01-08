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