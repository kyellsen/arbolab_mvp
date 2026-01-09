import shutil
import sys
from pathlib import Path

# Add package source to path
sys.path.append("/mnt/data/kyellsen/410_Packages/arbolab_mvp/packages/arbolab/src")

from arbolab.lab import Lab
from arbolab.models.core import UnitOfMeasurement, ObservedProperty, SensorModel, TreeSpecies
from arbolab.models.sys import SysMetadata

TARGET_DIR = Path("/mnt/data/kyellsen/410_Packages/arbolab_mvp/packages/arbolab/test_catalog_workspace")

def cleanup():
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)

def verify_seeding():
    print(f"Creating Lab at {TARGET_DIR}...")
    lab = Lab.open(workspace_root=TARGET_DIR)
    
    with lab.database.session() as session:
        # Check Version
        version = session.get(SysMetadata, "catalog_version")
        print(f"Catalog Version: {version.value if version else 'MISSING'}")
        
        # Check Counts
        units = session.query(UnitOfMeasurement).count()
        props = session.query(ObservedProperty).count()
        sensors = session.query(SensorModel).count()
        trees = session.query(TreeSpecies).count()
        
        print(f"Units: {units}")
        print(f"Properties: {props}")
        print(f"Sensor Models: {sensors}")
        print(f"Tree Species: {trees}")
        
        assert version is not None
        assert units >= 3
        assert props >= 3
        assert sensors >= 2
        assert trees >= 3
        
    print("✅ Catalog Seeding Verified Successfully.")

if __name__ == "__main__":
    print("Starting verification script...", flush=True)
    try:
        cleanup()
        verify_seeding()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
    finally:
        cleanup()
        print("Done.", flush=True)
