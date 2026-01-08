from sqlalchemy import select
from arbolab.lab import Lab
from arbolab.config import load_config
from arbolab.models.core import Project, Tree, Thing, Experiment

def seed_data():
    config = load_config()
    workspace_root = config.data_root / "workspace"
    lab = Lab.open(workspace_root)
    
    with lab.database.session() as session:
        # Check if project exists
        stmt = select(Project)
        existing_project = session.execute(stmt).scalars().first()
        
        if not existing_project:
            print("Seeding project...")
            project = Project(name="Stadtpark Süd", description="Main research area")
            session.add(project)
            session.flush() # ensure ID
            
            print("Seeding trees...")
            for i in range(1, 11):
                thing = Thing(project_id=project.id, kind="tree", name=f"Tree #{i}")
                session.add(thing)
                session.flush()
                tree = Tree(id=thing.id)
                session.add(tree)
            
            print("Seeding experiment...")
            experiment = Experiment(project_id=project.id, name="Soil Analysis 2026")
            session.add(experiment)
            
            session.commit()
            print("Seeding complete.")
        else:
            print(f"Project '{existing_project.name}' already exists. Skipping seed.")

if __name__ == "__main__":
    seed_data()
