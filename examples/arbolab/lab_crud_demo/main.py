"""
CRUD Demo Lab Example

Usage:
  This script relies on the 'arbolab' and 'arbolab-logger' packages in the workspace.
  You must run it within the configured environment using `uv run` or by ensuring PYTHONPATH is set.

  Command:
    uv run python examples/arbolab/lab_crud_demo/main.py
"""
import shutil
from pathlib import Path
from datetime import datetime

from arbolab.lab import Lab, LabRole
from arbolab.models.core import Project
from arbolab_logger import LoggerConfig, configure_logger, get_logger

# 1. Setup Logging
configure_logger(LoggerConfig(
    level="DEBUG", 
    colorize=True,
    # Arbolab automatically handles file logging to workspace/logs/
))

logger = get_logger("crud_demo")

def main():
    # Define roots
    base_root = Path("examples/arbolab/lab_crud_demo/example_workspace").resolve()
    input_root = base_root / "input"
    workspace_root = base_root / "workspace"
    results_root = base_root / "results"

    # Cleanup for clean run (Persist Input!)
    if workspace_root.exists():
        shutil.rmtree(workspace_root)
    if results_root.exists():
        shutil.rmtree(results_root)
    
    # Ensure input exists (part of repo usually, but ensure here)
    input_root.mkdir(parents=True, exist_ok=True)
    
    # 2. Open Lab
    lab = Lab.open(
        workspace_root=None,
        base_root=base_root,
        role=LabRole.ADMIN
    )

    # 3. Create Project
    logger.info("--- Creating Project ---")
    project = lab.define_project(name="CRUD Demo Project", description="Demonstrating CRUD")
    logger.info(f"Created: {project}")

    # 4. Create Experiment
    logger.info("--- Creating Experiment ---")
    experiment = lab.define_experiment(project_id=project.id, name="Experiment A", start_time=datetime.now())
    logger.info(f"Created: {experiment}")

    # 5. Add Trees (Things + Tree subtype)
    logger.info("--- Adding Trees ---")
    
    # Let's create a species first
    species = lab.define_tree_species(name="Oak")

    trees = []
    for i in range(3):
        # In the Recipe-Pattern, we explicitly define Thing then Tree
        thing = lab.define_thing(project_id=project.id, name=f"Tree {i+1}", kind="tree")
        tree = lab.define_tree(id=thing.id, species_id=species.id)
        trees.append(tree)
        # tree.thing might not be loaded, use thing directly for logging
        logger.info(f"Created Tree: {thing} (Species: {species})")

    # 6. Read Tree as Dictionary
    logger.info("--- Reading Tree as Dict ---")
    # Entity objects still have to_dict() for inspection
    tree_dict = tree.to_dict()
    logger.info(f"Tree Dict: {tree_dict}")

    # 7. Delete a Tree
    logger.info("--- Deleting a Tree ---")
    to_delete = trees.pop()
    lab.remove_tree(id=to_delete.id)
    logger.info(f"Deleted Tree {to_delete.id}.")

    # 8. Create Second Experiment
    logger.info("--- Creating Second Experiment ---")
    exp2 = lab.define_experiment(project_id=project.id, name="Experiment B (temp)", start_time=datetime.now())
    logger.info(f"Created: {exp2}")

    # 9. Delete Second Experiment
    logger.info("--- Deleting Second Experiment ---")
    lab.remove_experiment(id=exp2.id)
    logger.info(f"Deleted Experiment {exp2.id}.")

    # 10. Update Project
    logger.info("--- Renaming Project ---")
    logger.info(f"Old Name: {project.name}")
    lab.modify_project(id=project.id, name="Renamed Project")
    
    # Reload project to see changes
    with lab.database.session() as session:
        project = Project.get(session, project.id)
        logger.info(f"New Name: {project.name}")

    logger.info("CRUD Demo Complete.")

if __name__ == "__main__":
    main()
