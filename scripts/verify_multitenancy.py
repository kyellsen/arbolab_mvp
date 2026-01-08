import sys
import os
from pathlib import Path
from uuid import uuid4

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "packages/core/src"))

print("Starting verification... (DEBUG)", file=sys.stderr)

try:
    from sqlmodel import Session, SQLModel, create_engine, select
    from apps.web.models.auth import User, Workspace
    from apps.web.core.paths import resolve_workspace_paths, ensure_workspace_paths
    from apps.web.core.database import engine
    from arbolab.config import load_config
    print("Imports successful", file=sys.stderr)
except Exception as e:
    print(f"Import Error: {e}", file=sys.stderr)
    sys.exit(1)

def test_multitenancy():
    try:
        print("Initializing DB...", file=sys.stderr)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Create User
        # Note: In real app, ID is auto-generated if not provided, but we can provide for test
        user = User(email=f"test_{uuid4()}@example.com", hashed_password="pw")
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"Created User: {user.id} (Type: {type(user.id)})")
        
        # Check Workspace creation
        stmt = select(Workspace).where(Workspace.owner_id == user.id)
        ws = session.exec(stmt).first()
        if not ws:
            print("No workspace found, creating default...")
            ws = Workspace(name="Default WS", owner_id=user.id)
            session.add(ws)
            session.commit()
            session.refresh(ws)
        print(f"Workspace: {ws.id} (Owner: {ws.owner_id})")
        
        # Resolve Paths
        paths = resolve_workspace_paths(user.id, ws.id)
        print(f"Resolved Workspace Root: {paths.workspace_root}")
        
        # Verify Path Structure
        config = load_config()
        # config.data_root might be relative, ensure absolute for comparison
        expected_base = config.data_root.resolve() / str(user.id) / str(ws.id)
        assert paths.workspace_root == expected_base / "workspace"
        
        # Ensure Paths
        ensure_workspace_paths(paths)
        assert paths.workspace_root.exists()
        assert paths.input_root.exists()
        assert paths.results_root.exists()
        print("Directory isolation verified: Directories exist.")
        
        # Clean up (optional, but good for local dev)
        # shutil.rmtree(expected_base) 

if __name__ == "__main__":
    test_multitenancy()
