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

ArboLab supports two development workflows: **Full Dev Container** (Recommended) or **Hybrid / Local**.

### Option A: Full Dev Container (Recommended)

This method ensures an identical environment for all developers (Python 3.12, uv, PostgreSQL, Playwright).

1.  **Open in VS Code**:
    - Open the project folder.
    - Click **"Reopen in Container"** when prompted (or use the Command Palette: `Dev Containers: Reopen in Container`).
    - _Note for Antigravity/Google IDE users: The environment is automatically detected._

2.  **Run the App**:
    Inside the container's integrated terminal:
    ```bash
    uv run uvicorn apps.web.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The app will be available at [http://localhost:8000](http://localhost:8000).

### Option B: Hybrid / Local

Run the infrastructure (Postgres) via Docker/Podman, but execute the Python code on your host machine.

1.  **Prerequisites**:
    - Install **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    - Install **Podman** (or Docker) and `podman-compose`.

2.  **Setup Local Environment**:
    Run the setup script to create the `.venv` and install dependencies:

    ```bash
    ./setup.sh
    ```

3.  **Start Infrastructure**:
    Use the helper script to start the database (and optionally reset data):

    ```bash
    ./podman.sh
    ```

    _Alternatively, strictly for starting without reset: `podman-compose up -d`_

4.  **Run the App**:
    ```bash
    source .venv/bin/activate
    uv run uvicorn apps.web.main:app --host 0.0.0.0 --port 8000 --reload
    ```

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
