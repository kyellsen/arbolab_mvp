from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlmodel import select, Session as SaasSession
from typing import Any
from uuid import UUID

from apps.web.core.domain import list_entities, get_entity, create_entity, update_entity, delete_entity
from apps.web.models.auth import Workspace, UserWorkspaceAssociation
from apps.web.models.user import User
from apps.web.core.lab_cache import get_cached_lab
from apps.web.core.database import get_session as get_saas_session
from arbolab.lab import Lab
from arbolab.core.security import LabRole
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/entities", tags=["entities"])

# --- Dependency Injection for Multi-Tenancy ---

async def get_current_user_id(request: Request) -> UUID:
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        # Cast to string safely to handle legacy integer IDs or other types
        # This prevents AttributeError in UUID constructor and allows ValueError to catch invalid formats
        return UUID(str(user_data["id"]))
    except (ValueError, TypeError, KeyError):
        # KeyError if "id" is missing
        # ValueError/TypeError if UUID conversion fails
        request.session.clear() # Clear the invalid session
        raise HTTPException(status_code=401, detail="Invalid user session")

# User import handled at top of file

async def get_current_user(
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    session: SaasSession = Depends(get_saas_session)
) -> User:
    """Verifies user existence in DB to prevent ghost sessions (session exists, user deleted)."""
    user = session.get(User, user_id)
    if not user:
        # Clear invalid session and force re-login
        request.session.clear()
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ...

async def get_current_workspace(
    request: Request,
    user: User = Depends(get_current_user),
    session: SaasSession = Depends(get_saas_session)
) -> Workspace:
    """
    Determines the current active workspace for the user.
    Checks session['active_workspace_id'] first, then user.last_active_workspace_id,
    then falls back to the earliest workspace.
    """
    user_id = user.id

    def _fetch_workspace(workspace_id: UUID) -> Workspace | None:
        stmt = (
            select(Workspace)
            .join(UserWorkspaceAssociation)
            .where(Workspace.id == workspace_id)
            .where(UserWorkspaceAssociation.user_id == user_id)
        )
        return session.exec(stmt).first()

    workspace = None
    # 1. Try Session
    active_ws_id = request.session.get("active_workspace_id")
    if active_ws_id:
        try:
            workspace = _fetch_workspace(UUID(active_ws_id))
        except (ValueError, TypeError):
            workspace = None

    # 2. Try persisted last active workspace
    if not workspace and user.last_active_workspace_id:
        workspace = _fetch_workspace(user.last_active_workspace_id)

    # 3. Fallback: First available
    if not workspace:
        stmt = (
            select(Workspace)
            .join(UserWorkspaceAssociation)
            .where(UserWorkspaceAssociation.user_id == user_id)
            .order_by(Workspace.created_at)
        )
        workspace = session.exec(stmt).first()
    
    if not workspace:
        # Migration/Onboarding: Create default workspace
        # Create Workspace AND Association (ADMIN)
        from arbolab.core.security import LabRole
        workspace = Workspace(name="Default Workspace")
        session.add(workspace)
        session.commit()
        session.refresh(workspace)
        
        # Link as Admin
        assoc = UserWorkspaceAssociation(
            user_id=user_id, 
            workspace_id=workspace.id, 
            role=LabRole.ADMIN
        )
        session.add(assoc)
        session.commit()

    request.state.workspace_id = workspace.id
    request.session["active_workspace_id"] = str(workspace.id)
    if user.last_active_workspace_id != workspace.id:
        user.last_active_workspace_id = workspace.id
        session.add(user)
        session.commit()
    return workspace

def get_lab(
    user_id: UUID = Depends(get_current_user_id),
    workspace: Workspace = Depends(get_current_workspace),
    session: SaasSession = Depends(get_saas_session) 
) -> Lab:
    """
    Instantiates the Lab for the specific isolated workspace.
    Enforces path isolation.
    """
    # 1. Get Role
    stmt = select(UserWorkspaceAssociation).where(
        UserWorkspaceAssociation.user_id == user_id,
        UserWorkspaceAssociation.workspace_id == workspace.id
    )
    assoc = session.exec(stmt).first()
    if not assoc:
         # Should ideally be caught by get_current_workspace, but strict check here
         raise HTTPException(status_code=403, detail="Access denied to workspace")

    try:
        return get_cached_lab(workspace.id, assoc.role)
    except ValueError as e:
        # Security violation (Path traversal)
        raise HTTPException(status_code=403, detail=str(e))

def get_db_session(lab: Lab = Depends(get_lab)):
    """Yields a session for the specific Lab (DuckDB)."""
    with lab.database.session() as session:
        yield session

# Helper for explicit check
def ensure_admin(lab: Lab):
    if lab.role != LabRole.ADMIN:
        raise HTTPException(status_code=403, detail="Read-only access: Only ADMINs can modify data.")

@router.get("/{entity_type}")
async def api_list_entities(entity_type: str, search: str = None, tag: str = None, lab: Lab = Depends(get_lab)):
    with lab.database.session() as session:
        try:
            return await list_entities(session, entity_type, search=search, tag=tag)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.get("/{entity_type}/{entity_id}")
async def api_get_entity(entity_type: str, entity_id: int, lab: Lab = Depends(get_lab)):
    with lab.database.session() as session:
        entity = await get_entity(session, entity_type, entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity

@router.post("/{entity_type}")
async def api_create_entity(entity_type: str, data: dict[str, Any], lab: Lab = Depends(get_lab)):
    ensure_admin(lab)
    with lab.database.session() as session:
        try:
            return await create_entity(session, entity_type, data, lab=lab)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.put("/{entity_type}/{entity_id}")
async def api_update_entity(entity_type: str, entity_id: int, data: dict[str, Any], lab: Lab = Depends(get_lab)):
    ensure_admin(lab)
    with lab.database.session() as session:
        try:
            entity = await update_entity(session, entity_type, entity_id, data, lab=lab)
            if not entity:
                raise HTTPException(status_code=404, detail="Entity not found")
            return entity
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{entity_type}/{entity_id}")
async def api_delete_entity(entity_type: str, entity_id: int, lab: Lab = Depends(get_lab)):
    ensure_admin(lab)
    with lab.database.session() as session:
        try:
            success = await delete_entity(session, entity_type, entity_id, lab=lab)
            if not success:
                raise HTTPException(status_code=404, detail="Entity not found")
            return {"status": "deleted"}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.get("/recipes/export")
async def api_export_recipe(lab: Lab = Depends(get_lab)):
    """Downloads the current recipe JSON file."""
    recipe_path = lab.layout.recipe_path("current.json")
    if not recipe_path.exists():
        raise HTTPException(status_code=404, detail="Recipe file not found")
    return FileResponse(
        path=recipe_path,
        media_type="application/json",
        filename="current.json",
    )
