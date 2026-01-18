# Arbolab Examples

This directory contains examples and demonstrations for using [Arbolab](../../packages/arbolab/README.md).

## Structure

- **`arbolab/`**: Core library examples.
  - **`lab_crud_demo/`**: A complete script demonstrating Create, Read, Update, Delete operations on a Lab project.
  - **`lab_open_minimal/`**: A minimal example showing how to initialize a Lab and ensure persistence.
  - **`local_workflow.ipynb`**: A Jupyter notebook demonstrating a local workflow.

## Data Structure

Each example creates a local `example_workspace/` directory containing:

- `input/`: Raw input data (preserves across runs, can be committed).
- `workspace/`: Internal Lab state (database, config). Cleared on each run.
- `results/`: Analysis output. Cleared on each run.

**Note**: `example_workspace/` is ignored by git, except for `input/` data which is intended to be shared.

## Running Examples

All examples should be run from the root of the monolithic repository using `uv` to ensure the environment is correctly set up.
Logs are written to `example_workspace/workspace/lab.log` (DEBUG level).

### CRUD Demo

```bash
uv run python examples/arbolab/lab_crud_demo/main.py
```

### Minimal Lab

```bash
uv run python examples/arbolab/lab_open_minimal/main.py
```
