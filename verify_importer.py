import sys
import shutil
from pathlib import Path

# Fix path to include core and logger
root = Path(__file__).parent
sys.path.insert(0, str(root / "packages/core/src"))
# Assuming logger is installed or reachable. If not, we might fail. 
# But 'uv sync' should have installed deps.

try:
    from arbolab.lab import Lab
    from arbolab.models.core import Project, Experiment
    import polars as pl
except ImportError as e:
    with open("verification_result.txt", "a") as f:
        f.write(f"ImportError: {e}\n")
    # Try adding likely paths
    sys.path.append(str(root / "packages/arbolab-logger/src"))
    from arbolab.lab import Lab
    from arbolab.models.core import Project, Experiment
    import polars as pl

def log(msg):
    with open("verification_result.txt", "a") as f:
        f.write(str(msg) + "\n")

def run_test():
    with open("verification_result.txt", "w") as f:
        f.write("Starting Verification\n")
    
    tmp_path = Path("temp_verif_ws")
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    tmp_path.mkdir()

    try:
        ws = tmp_path / "workspace"
        input_ = tmp_path / "input"
        results = tmp_path / "results"
        
        log("Opening Lab...")
        lab = Lab.open(workspace_root=ws, input_root=input_, results_root=results)
        
        # 1. Create a dummy metadata package in input_root
        pkg_dir = input_root / "metadata"
        pkg_dir.mkdir(parents=True)
        
        # Create projects.csv
        projects_csv = pkg_dir / "projects.csv"
        pl.DataFrame({
            "id": [1],
            "name": ["Test Project"],
            "description": ["Integration Test"]
        }).write_csv(projects_csv)
        
        # Create experiments.csv
        experiments_csv = pkg_dir / "experiments.csv"
        pl.DataFrame({
            "id": [10],
            "project_id": [1],
            "name": ["Exp 1"],
            "description": ["First experiment"]
        }).write_csv(experiments_csv)
        
        # Create datapackage.json
        datapackage = {
            "name": "test-package",
            "resources": [
                {"name": "projects", "path": "projects.csv"},
                {"name": "experiments", "path": "experiments.csv"}
            ]
        }
        
        pkg_file = pkg_dir / "datapackage.json"
        with open(pkg_file, "w") as f:
            import json
            json.dump(datapackage, f)
            
        log("Importing Metadata...")
        # 2. Run Import
        stats = lab.import_metadata(pkg_file)
        log(f"Import Stats: {stats}")
        
        assert stats.get("projects", {}).get("count") == 1
        assert stats.get("experiments", {}).get("count") == 1
        
        # 3. Verify in DB
        log("Verifying Database...")
        with lab.database.session() as session:
            proj = session.get(Project, 1)
            assert proj is not None
            assert proj.name == "Test Project"
            log("Project Verified.")
            
            exp = session.get(Experiment, 10)
            assert exp is not None
            assert exp.project_id == 1
            assert exp.name == "Exp 1"
            log("Experiment Verified.")
            
        log("SUCCESS")
    except Exception as e:
        log(f"FAILED: {e}")
        import traceback
        with open("verification_result.txt", "a") as f:
            traceback.print_exc(file=f)
    finally:
        if tmp_path.exists():
            shutil.rmtree(tmp_path)

if __name__ == "__main__":
    run_test()
