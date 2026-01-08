import sys
from sqlmodel import Session, select
from apps.web.core.database import engine
from apps.web.models.auth import User, Workspace

try:
    with Session(engine) as session:
        user = session.exec(select(User)).first()
        if user:
            workspaces = session.exec(select(Workspace).where(Workspace.owner_id == user.id)).all()
            print(f"User: {user.email}")
            print(f"Workspace Count: {len(workspaces)}")
            for w in workspaces:
                print(f" - {w.name} ({w.id})")
        else:
            print("No user found")
except Exception as e:
    print(f"Error: {e}")
