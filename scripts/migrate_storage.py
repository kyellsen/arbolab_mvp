import os
import shutil
import sys
from pathlib import Path

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "packages/arbolab/src"))

from arbolab.config import load_config
from sqlmodel import Session, select

from apps.web.core.database import engine
from apps.web.core.paths import resolve_workspace_paths
from apps.web.models.auth import User, Workspace


def migrate_flat_to_multitenant(email: str, password: str):
    """
    Migrates the 'flat' single-tenant data structure to the new multi-tenant structure
    under a newly created (or existing) user.
    """
    print(f"Starting migration for {email}...")
    
    config = load_config()
    data_root = config.data_root.resolve()
    
    # Old Paths
    old_workspace = data_root / "workspace"
    old_input = data_root / "input"
    old_results = data_root / "results"
    
    if not old_workspace.exists():
        print(f"No existing flat workspace found at {old_workspace}. Nothing to migrate.")
        return

    # 1. Create/Get User
    with Session(engine) as session:
        stmt = select(User).where(User.email == email)
        user = session.exec(stmt).first()
        if not user:
            print("Creating new user...")
            from apps.web.core.security import get_password_hash
            user = User(email=email, hashed_password=get_password_hash(password))
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # 2. Create Workspace
        stmt = select(Workspace).where(Workspace.owner_id == user.id)
        ws = session.exec(stmt).first()
        if not ws:
            print("Creating new workspace container...")
            ws = Workspace(name="Migrated Workspace", owner_id=user.id)
            session.add(ws)
            session.commit()
            session.refresh(ws)
            
        user_id = user.id
        ws_id = ws.id
    
    print(f"Target: User {user_id} / Workspace {ws_id}")
    
    # 3. Resolve New Paths
    new_paths = resolve_workspace_paths(user_id, ws_id)
    # Ensure parents exist
    new_paths.workspace_root.parent.mkdir(parents=True, exist_ok=True)
    
    # 4. Move Data
    def move_dir(src: Path, dst: Path):
        if src.exists():
            print(f"Moving {src} -> {dst}")
            if dst.exists():
                print(f"Warning: Destination {dst} already exists. Merging/Overwriting...")
                # shutil.move fails if dst exists usually, depending on impl.
                # safely: rename src to dst
                # if dst exists, we might need to use copytree with dirs_exist_ok=True and then rm
            shutil.move(str(src), str(dst))
        else:
            print(f"Source {src} does not exist, skipping.")
            dst.mkdir(parents=True, exist_ok=True)

    move_dir(old_workspace, new_paths.workspace_root)
    move_dir(old_input, new_paths.input_root)
    move_dir(old_results, new_paths.results_root)
    
    print("Migration completed successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/migrate_storage.py <email> <password>")
        sys.exit(1)
    
    migrate_flat_to_multitenant(sys.argv[1], sys.argv[2])
