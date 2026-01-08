from sqlalchemy import select, func
from arbolab.lab import Lab
from arbolab.config import load_config
from arbolab.models.core import Project, Experiment, Tree, Sensor

def check_counts():
    config = load_config()
    workspace_root = config.data_root / "workspace"
    lab = Lab.open(workspace_root)
    
    with lab.database.session() as session:
        projects = session.execute(select(func.count(Project.id))).scalar()
        experiments = session.execute(select(func.count(Experiment.id))).scalar()
        trees = session.execute(select(func.count(Tree.id))).scalar()
        sensors = session.execute(select(func.count(Sensor.id))).scalar()
        
        print(f"Projects: {projects}")
        print(f"Experiments: {experiments}")
        print(f"Trees: {trees}")
        print(f"Sensors: {sensors}")

if __name__ == "__main__":
    check_counts()
