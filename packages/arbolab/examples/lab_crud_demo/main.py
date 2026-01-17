"""
CRUD Demo Lab Example

Usage:
  This script relies on the 'arbolab' and 'arbolab-logger' packages in the workspace.
  You must run it within the configured environment using `uv run` or by ensuring PYTHONPATH is set.

  Command:
    uv run python packages/arbolab/examples/lab_crud_demo/main.py
"""
import shutil
from pathlib import Path

from arbolab.lab import Lab
from arbolab.models.core import Project
from arbolab_logger import LoggerConfig, configure_logger, get_logger

# 1. Setup Logging
configure_logger(LoggerConfig(
    level="INFO", 
    colorize=True, 
    log_to_file=False
))

logger = get_logger("crud_demo")

def main():
    # Define roots
    base_root = Path("packages/arbolab/examples/lab_crud_demo/example_workspace")
    input_root = base_root / "input"
    workspace_root = base_root / "workspace"
    results_root = base_root / "results"

    # Cleanup for clean run
    if base_root.exists():
        shutil.rmtree(base_root)
    
    input_root.mkdir(parents=True)
    
    # 2. Open Lab
    lab = Lab.open(
        workspace_root=workspace_root,
        input_root=input_root,
        results_root=results_root
    )

    # 3. Create Project
    logger.info("--- Creating Project ---")
    project = lab.define_project(name="CRUD Demo Project", description="Demonstrating CRUD")
    logger.info(f"Created: {project}")

    # 4. Create Experiment
    logger.info("--- Creating Experiment ---")
    experiment = lab.define_experiment(project_id=project.id, name="Experiment A")
    logger.info(f"Created: {experiment}")

    # 5. Add Trees (Things + Tree subtype)
    logger.info("--- Adding Trees ---")
    
    # Let's create a species first
    species = lab.define_tree_species(name="Oak")

    trees = []
    for i in range(3):
        # In the Recipe-Pattern, we define the tree which handles the thing creation
        tree = lab.define_tree(project_id=project.id, species_id=species.id, name=f"Tree {i+1}")
        trees.append(tree)
        logger.info(f"Created Tree: {tree.thing} (Species: {species})")

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
    exp2 = lab.define_experiment(project_id=project.id, name="Experiment B (temp)")
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
