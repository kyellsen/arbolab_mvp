import sys
import traceback

try:
    print("Starting seed script...")
    from sqlmodel import Session, select
    from apps.web.core.database import engine
    from apps.web.models.auth import User, Workspace
    from uuid import UUID

    def seed_workspaces():
        with Session(engine) as session:
            # Get the first user (usually the one created by default or logged in)
            user = session.exec(select(User)).first()
            if not user:
                print("No user found! Please register/login first.")
                return

            print(f"Seeding workspaces for user: {user.email} ({user.id})")

            # Check existing workspaces
            workspaces = session.exec(select(Workspace).where(Workspace.owner_id == user.id)).all()
            existing_names = {w.name for w in workspaces}

            desired_workspaces = ["Lab A (City)", "Lab B (Forest)", "Lab C (Desert)"]
            
            for name in desired_workspaces:
                if name not in existing_names:
                    print(f"Creating workspace: {name}")
                    ws = Workspace(name=name, owner_id=user.id)
                    session.add(ws)
                else:
                    print(f"Workspace exists: {name}")
            
            session.commit()
            print("Seeding complete.")

    if __name__ == "__main__":
        seed_workspaces()
except Exception:
    traceback.print_exc()
