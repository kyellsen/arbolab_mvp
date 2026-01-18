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

## 🚀 Development Setup

## 🚀 Development Setup

ArboLab supports three main ways to run the application to suit different needs.

### 1. Full Dev Container (Recommended)

**Best for**: Consistency, VS Code users, easy setup.
This method runs _everything_ (Python, DB, Tools) inside containers managed by VS Code.

1.  **Open in VS Code**: Open the folder and click **"Reopen in Container"**.
2.  **Run**: Open the integrated terminal and run:
    ```bash
    uv run uvicorn apps.web.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    (The environment is automatically activated and dependencies synced).

### 2. Hybrid / Local (Python on Host)

**Best for**: Debugging, Jupyter Notebooks, native performance.
You run Python locally on your machine, but use Docker/Podman for the Database.

1.  **Setup Python**:

    ```bash
    ./setup.sh
    ```

    _Creates `.venv` and installs dependencies via uv._

2.  **Start Database**:

    ```bash
    ./podman.sh
    ```

    _Starts Postgres using `compose.yaml`. Deleting data? see script details._

3.  **Run App**:
    ```bash
    source .venv/bin/activate
    uv run uvicorn apps.web.main:app --host 0.0.0.0 --port 8000 --reload
    ```

### 3. Production Simulation

**Best for**: verifying the final build, security checks.
This uses the production Dockerfile (non-root user) and `compose.prod.yaml`.

```bash
docker compose -f compose.prod.yaml up --build -d
```

_Note: This does NOT hot-reload code changes. You must rebuild to see changes._

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
