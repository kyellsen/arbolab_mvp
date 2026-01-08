# Recipe-First Architecture

The ArboLab "Recipe-First" architecture ensures that every change to the Lab state (Domain Entities) is recorded as a reproducible, transpilable step.

## Core Philosophy

1.  **State is Procedural**: The current state of a Lab is defined by the linear sequence of actions (Recipes) applied to it.
2.  **Explicit Recording**: Every write operation (Create, Update, Delete) must go through the `RecipeExecutor`.
3.  **Transpilability**: A Recipe can be converted into a standalone Python script that reproduces the exact state of the Lab.

## Components

- **`RecipeStep`**: A single action (e.g., `define_project`, `modify_sensor`).
- **`Recipe`**: A JSON collection of steps saved in `workspace_root/recipes/current.json`.
- **`RecipeExecutor`**: The engine that runs a step and records it to the log.
- **`RecipeTranspiler`**: Generates Python code from a Recipe.

## Usage Guidelines

### Backend (Lab API)

Always use the dedicated recipe-aware methods on the `Lab` object for modifications:

```python
with Lab.open("path/to/ws") as lab:
    # This records a 'define_project' step
    project = lab.define_project(name="My Forest Study")
    
    # This records a 'define_sensor' step
    sensor = lab.define_sensor(name="Sensor_A", model="MEMS_V1")
```

### Generic Dispatch

For entities that don't have explicit wrapper methods, use `execute_step`:

```python
lab.execute_step("define_experimental_unit", {"name": "Unit_1", "project_id": 1})
```

### Frontend (Apps/Web)

The web routers should never touch models or database sessions directly for write operations. Instead, they must call the `Lab` methods.

**DO:**
```python
# In api.py
@router.post("/project")
async def create_project(data: dict, lab: Lab = Depends(get_lab)):
    return lab.define_project(**data)
```

**DON'T:**
```python
# legacy direct write
session.add(Project(**data))
session.commit()
```

## Why Recipes?

- **Audit Trail**: See exactly who changed what and when.
- **Reproducibility**: Re-run the same experiment setup on a clean dataset.
- **Portability**: Scientific workflows can be exported as code and shared with colleagues.
