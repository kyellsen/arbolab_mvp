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
from arbolab.models.core import Experiment, Project, Thing, Tree, TreeSpecies
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
    base_root = Path("./examples/arbolab/lab_crud_demo/example_workspace")
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

    with lab.database.session() as session:
        # 3. Create Project
        logger.info("--- Creating Project ---")
        project = Project.create(session, name="CRUD Demo Project", description="Demonstrating CRUD")
        session.flush() # Ensure ID availability
        logger.info(f"Created: {project}")

        # 4. Create Experiment
        logger.info("--- Creating Experiment ---")
        experiment = Experiment.create(session, project_id=project.id, name="Experiment A")
        session.flush()
        logger.info(f"Created: {experiment}")

        # 5. Add Trees (Things + Tree subtype)
        logger.info("--- Adding Trees ---")
        
        # Helper to create a tree (requires creating Thing first or at same time)
        # Note: In our model, Tree inherits from Thing table-wise/polymorphically via joined inheritance usually,
        # but in 'core.py', Tree is a separate model joined to Thing.
        # Thing(kind='tree') <- Tree(id=thing.id)
        
        # Let's create a species first
        species = TreeSpecies.create(session, name="Oak")
        session.flush()

        trees = []
        for i in range(3):
            # Create Thing parent
            thing = Thing.create(session, project_id=project.id, kind="tree", name=f"Tree {i+1}")
            session.flush()
            
            # Create Tree subtype
            tree = Tree.create(session, id=thing.id, species_id=species.id)
            session.flush()
            
            trees.append(tree)
            logger.info(f"Created Tree: {thing} (Species: {species})")

        # 6. Read Tree as Dictionary
        logger.info("--- Reading Tree as Dict ---")
        tree_dict = trees[0].to_dict()
        thing_dict = trees[0].thing.to_dict()
        logger.info(f"Tree Dict: {tree_dict}")
        logger.info(f"Thing Dict: {thing_dict}")

        # 7. Delete a Tree
        logger.info("--- Deleting a Tree ---")
        to_delete = trees.pop() # Remove last one
        
        # We need to delete the Thing, cascade should handle the Tree, 
        # or we delete explicitly depending on configuration.
        # Based on core.py: `tree: Mapped[Tree | None] = relationship(..., cascade="all, delete-orphan")`
        # So deleting the Thing should delete the Tree.
        thing_to_delete = to_delete.thing
        thing_id_deleted = thing_to_delete.id
        thing_to_delete.delete(session)
        session.flush()

        deleted_thing = Thing.get(session, thing_id_deleted)
        logger.info(f"Deleted Tree {thing_id_deleted}. Exists? {deleted_thing is not None}")

        # 8. Create Second Experiment
        logger.info("--- Creating Second Experiment ---")
        exp2 = Experiment.create(session, project_id=project.id, name="Experiment B (temp)")
        session.flush()
        logger.info(f"Created: {exp2}")

        # 9. Delete Second Experiment
        logger.info("--- Deleting Second Experiment ---")
        exp2_id = exp2.id
        exp2.delete(session)
        session.flush()
        
        deleted_exp = Experiment.get(session, exp2_id)
        logger.info(f"Deleted Experiment {exp2_id}. Exists? {deleted_exp is not None}")

        # 10. Update Project
        logger.info("--- Renaming Project ---")
        logger.info(f"Old Name: {project.name}")
        project.update(session, name="Renamed Project")
        session.flush()
        logger.info(f"New Name: {project.name}")

    logger.info("CRUD Demo Complete.")

if __name__ == "__main__":
    main()
