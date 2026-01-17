import tomllib
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select, text

from apps.web.core.lab_cache import get_cached_lab
from apps.web.models.auth import UserWorkspaceAssociation
from apps.web.routers.api import (
    get_saas_session,
)

router = APIRouter(prefix="/api/system", tags=["system"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # apps/web/ -> arbolab_mvp root? 
# Wait, file is at apps/web/routers/system.py
# .parent = apps/web/routers
# .parent.parent = apps/web
# .parent.parent.parent = arbolab_mvp root (roughly)

# Let's use a safer relative path finder or absolute path if possible, but relative to this file is fine for dev.
# arbolab_mvp root is 3 levels up from apps/web? 
# apps/web/routers/system.py -> routers -> web -> apps -> arbolab_mvp 
# That is 4 levels up. 

def get_project_root() -> Path:
    # returns /mnt/data/.../arbolab_mvp
    return Path(__file__).resolve().parent.parent.parent.parent

def get_version_from_toml(path: Path) -> str:
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "unknown")
    except Exception:
        return "unknown"

@router.get("/status")
async def get_system_status(
    request: Request,
    saas_session: Session = Depends(get_saas_session),
    # We make Lab optional because we might be in a state where no lab is open (e.g. dashboard list)
    # But usually the footer is present. If no lab is open, we just report global status.
):
    project_root = get_project_root()
    
    # 1. Versions
    web_version = get_version_from_toml(project_root / "apps/web/pyproject.toml")
    core_version = get_version_from_toml(project_root / "packages/arbolab/pyproject.toml")
    
    # 2. Postgres Status
    postgres_status = False
    try:
        saas_session.exec(text("SELECT 1"))
        postgres_status = True
    except Exception:
        postgres_status = False
        
    # 3. Lab / DuckDB Status & Role
    lab_status = False
    role_label = "No Lab"
    
    # Try to resolve lab context from session similar to other routers
    # We duplicate some logic here to avoid strict dependency failure if no workspace is active
    user_data = request.session.get("user")
    if user_data:
        try:
            user_id = UUID(str(user_data["id"]))
            active_ws_id = request.session.get("active_workspace_id")
            
            if active_ws_id:
                # Check association
                assoc = saas_session.exec(
                    select(UserWorkspaceAssociation)
                    .where(UserWorkspaceAssociation.user_id == user_id)
                    .where(UserWorkspaceAssociation.workspace_id == UUID(active_ws_id))
                ).first()
                
                if assoc:
                    role_label = assoc.role.value
                    
                    # Check DuckDB
                    # We don't want to crash if cache is empty or lab failed to load
                    try:
                        lab = get_cached_lab(UUID(active_ws_id), assoc.role)
                        if lab and lab.database:
                             # Minimal check: access property or run simple query
                             # lab.database.session() creates a session from engine. 
                             # We can just check if engine is initialized.
                             if getattr(lab.database, "_engine", None):
                                 lab_status = True
                    except Exception:
                        lab_status = False
        except Exception:
            pass

    return {
        "versions": {
            "web": web_version,
            "core": core_version
        },
        "postgres": postgres_status,
        "lab": lab_status,
        "role": role_label
    }
