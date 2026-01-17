
import os
import shutil
import sys
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Session, select

# Add project root to sys.path
sys.path.append(os.getcwd())

from arbolab.config import load_config

from apps.web.core.database import engine
from apps.web.models.auth import LabRole, UserWorkspaceAssociation


def migrate():
    print("Starting Migration: V1 (Nested) -> V2 (Flat RBAC)...")
    
    config = load_config()
    data_root = config.data_root.resolve()
    target_workspaces_root = data_root / "workspaces"
    target_workspaces_root.mkdir(parents=True, exist_ok=True)
    
    with Session(engine) as session:
        # 1. Fetch all workspaces using RAW SQL to get the 'owner_id' 
        # (since we removed it from the ORM model)
        # We also want the ID to find the folder
        
        try:
            result = session.exec(text("SELECT id, owner_id FROM workspace"))
            workspaces = result.all()
        except Exception as e:
            print(f"Error fetching workspaces (maybe column already gone?): {e}")
            workspaces = []

        print(f"Found {len(workspaces)} workspaces to migrate.")

        for row in workspaces:
            ws_id = UUID(str(row[0]))
            owner_id = UUID(str(row[1]))
            
            # --- A. Data Migration ---
            # Old Path: data_root / user_id / ws_id
            old_path = data_root / str(owner_id) / str(ws_id)
            new_path = target_workspaces_root / str(ws_id)
            
            if old_path.exists():
                if new_path.exists():
                    print(f"WARN: Target {new_path} already exists. Skipping move for {ws_id}.")
                else:
                    print(f"Moving {old_path} -> {new_path}")
                    shutil.move(old_path, new_path)
                    
                    # Cleanup old user dir if empty?
                    try:
                        old_user_dir = data_root / str(owner_id)
                        if not any(old_user_dir.iterdir()):
                            old_user_dir.rmdir()
                            print(f"Removed empty user dir: {old_user_dir}")
                    except Exception as e:
                        print(f"Could not remove user dir: {e}")
            # Check if it's already in the new location (partial migration?)
            elif new_path.exists():
                print(f"Workspace {ws_id} already in new location.")
            else:
                print(f"WARN: Source path {old_path} not found for workspace {ws_id}. Data might be missing.")

            # --- B. Schema Migration (Association) ---
            # Check if association already exists
            existing_assoc = session.exec(
                select(UserWorkspaceAssociation)
                .where(UserWorkspaceAssociation.user_id == owner_id)
                .where(UserWorkspaceAssociation.workspace_id == ws_id)
            ).first()
            
            if not existing_assoc:
                print(f"Creating ADMIN association for User {owner_id} -> Workspace {ws_id}")
                assoc = UserWorkspaceAssociation(
                    user_id=owner_id,
                    workspace_id=ws_id,
                    role=LabRole.ADMIN
                )
                session.add(assoc)
        
        session.commit()
        
        # --- C. Drop owner_id Column ---
        # Only do this if we are sure migration happened.
        print("Dropping 'owner_id' column from 'workspace' table...")
        try:
            session.exec(text("ALTER TABLE workspace DROP COLUMN owner_id"))
            session.commit()
            print("Column dropped.")
        except Exception as e:
            print(f"Skipping DROP COLUMN (already dropped?): {e}")
            session.rollback()

    print("Migration Complete.")

if __name__ == "__main__":
    migrate()
