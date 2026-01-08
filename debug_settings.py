import os
import sys
from pathlib import Path
from uuid import UUID
from sqlmodel import Session, create_engine, select
import yaml

# Add project root to sys.path
sys.path.append(os.getcwd())

from apps.web.models.user import User
from apps.web.models.auth import Workspace, UserWorkspaceAssociation
from arbolab.config import load_config, update_config

def verify_settings():
    print("--- Starting Verification ---")
    
    # 1. Setup Test DB
    db_path = Path("apps/web/data/saas.db")
    if not db_path.exists():
        # Fallback to current config
        config = load_config()
        db_path = config.data_root / "saas.db"
        
    database_url = f"sqlite:///{db_path.resolve()}"
    engine = create_engine(database_url)
    
    with Session(engine) as session:
        # 2. Test User Profile Update
        print("Testing Profile Update...")
        user = session.exec(select(User)).first()
        if not user:
            print("No user found in DB. Please run a migration/seed first.")
            return

        user.full_name = "Test User"
        user.organization = "Test Org"
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.full_name == "Test User"
        assert user.organization == "Test Org"
        print("✓ Profile Update Success")

        # 3. Test Lab Config Update
        print("Testing Lab Config Update...")
        workspace = session.exec(select(Workspace)).first()
        if workspace:
            from apps.web.core.paths import resolve_workspace_paths
            paths = resolve_workspace_paths(workspace.id)
            
            updates = {"enabled_plugins": ["ls3", "ptq"]}
            update_config(paths.workspace_root, updates)
            
            new_config = load_config(paths.workspace_root)
            assert "ls3" in new_config.enabled_plugins
            assert "ptq" in new_config.enabled_plugins
            print("✓ Lab Config Update Success")
        else:
            print("Skipping Workspace Config test (no workspace found)")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_settings()
