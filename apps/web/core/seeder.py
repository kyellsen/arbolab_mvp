import json
import logging
from pathlib import Path
from typing import List
from uuid import UUID

from sqlmodel import Session, select
from apps.web.core.database import engine
from apps.web.models.user import User, Workspace, UserWorkspaceAssociation
from apps.web.core.security import get_password_hash
from arbolab.core.security import LabRole

logger = logging.getLogger(__name__)

def run_seed():
    """
    Reads the JSON file and seeds the database with default users.
    Idempotent: Checks if users already exist by email.
    """
    seed_file = Path(__file__).parent.parent / "resources" / "seed" / "users.json"
    
    if not seed_file.exists():
        logger.warning(f"Seed file not found at {seed_file}")
        return

    try:
        with open(seed_file, "r") as f:
            seed_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read seed file: {e}")
        return

    with Session(engine) as session:
        for user_data in seed_data:
            email = user_data.get("email")
            if not email:
                continue

            # Check if user already exists
            statement = select(User).where(User.email == email)
            existing_user = session.exec(statement).first()

            if not existing_user:
                print(f"Seeding default user: {email}")
                logger.info(f"Seeding default user: {email}")
                
                # Create user
                password = user_data.get("password", "change_me_promptly")
                new_user = User(
                    email=email,
                    hashed_password=get_password_hash(password),
                    full_name=user_data.get("full_name"),
                    is_active=user_data.get("is_active", True)
                )
                session.add(new_user)
                session.commit()
                session.refresh(new_user)

                # Ensure user has at least one workspace
                # Check if associations exist (though for a new user they shouldn't)
                stmt_ws = select(Workspace).join(UserWorkspaceAssociation).where(UserWorkspaceAssociation.user_id == new_user.id)
                workspace = session.exec(stmt_ws).first()

                if not workspace:
                    # Create default workspace
                    new_workspace = Workspace(name="Default Workspace")
                    session.add(new_workspace)
                    session.commit()
                    session.refresh(new_workspace)

                    # Link user to workspace as ADMIN
                    association = UserWorkspaceAssociation(
                        user_id=new_user.id,
                        workspace_id=new_workspace.id,
                        role=LabRole.ADMIN
                    )
                    new_user.last_active_workspace_id = new_workspace.id
                    session.add(association)
                    session.add(new_user)
                    session.commit()
            else:
                # User exists, optionally ensure they have a workspace if they were seeded partially
                stmt_ws = select(Workspace).join(UserWorkspaceAssociation).where(UserWorkspaceAssociation.user_id == existing_user.id)
                workspace = session.exec(stmt_ws).first()
                
                if not workspace:
                    logger.info(f"Creating default workspace for existing seeded user: {email}")
                    new_workspace = Workspace(name="Default Workspace")
                    session.add(new_workspace)
                    session.commit()
                    session.refresh(new_workspace)

                    association = UserWorkspaceAssociation(
                        user_id=existing_user.id,
                        workspace_id=new_workspace.id,
                        role=LabRole.ADMIN
                    )
                    existing_user.last_active_workspace_id = new_workspace.id
                    session.add(association)
                    session.add(existing_user)
                    session.commit()
