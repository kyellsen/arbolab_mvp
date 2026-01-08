from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlmodel import select, Session as SaasSession
from typing import Any
from uuid import UUID

from apps.web.core.domain import list_entities, get_entity, create_entity, update_entity, delete_entity
from apps.web.models.auth import User, Workspace
from apps.web.core.paths import resolve_workspace_paths, ensure_workspace_paths
from apps.web.core.database import get_session as get_saas_session
from arbolab.lab import Lab
from pathlib import Path

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

async def get_current_workspace(
    user_id: UUID = Depends(get_current_user_id),
    session: SaasSession = Depends(get_saas_session)
) -> Workspace:
    """
    Determines the current active workspace for the user.
    MVP: Auto-selects the first workspace or creates a default one.
    """
    stmt = select(Workspace).where(Workspace.owner_id == user_id)
    workspace = session.exec(stmt).first()
    
    if not workspace:
        # Migration/Onboarding: Create default workspace
        workspace = Workspace(name="Default Workspace", owner_id=user_id)
        session.add(workspace)
        session.commit()
        session.refresh(workspace)
        
    return workspace

def get_lab(
    user_id: UUID = Depends(get_current_user_id),
    workspace: Workspace = Depends(get_current_workspace)
) -> Lab:
    """
    Instantiates the Lab for the specific isolated workspace.
    Enforces path isolation.
    """
    try:
        paths = resolve_workspace_paths(user_id, workspace.id)
        ensure_workspace_paths(paths)
        
        return Lab.open(
            workspace_root=paths.workspace_root,
            input_root=paths.input_root,
            results_root=paths.results_root
        )
    except ValueError as e:
        # Security violation (Path traversal)
        raise HTTPException(status_code=403, detail=str(e))

def get_db_session(lab: Lab = Depends(get_lab)):
    """Yields a session for the specific Lab (DuckDB)."""
    with lab.database.session() as session:
        yield session

@router.get("/{entity_type}")
async def api_list_entities(entity_type: str, search: str = None, tag: str = None, session: Session = Depends(get_db_session)):
    try:
        return await list_entities(session, entity_type, search=search, tag=tag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{entity_type}/{entity_id}")
async def api_get_entity(entity_type: str, entity_id: int, session: Session = Depends(get_db_session)):
    entity = await get_entity(session, entity_type, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.post("/{entity_type}")
async def api_create_entity(entity_type: str, data: dict[str, Any], session: Session = Depends(get_db_session)):
    try:
        return await create_entity(session, entity_type, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{entity_type}/{entity_id}")
async def api_update_entity(entity_type: str, entity_id: int, data: dict[str, Any], session: Session = Depends(get_db_session)):
    try:
        entity = await update_entity(session, entity_type, entity_id, data)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{entity_type}/{entity_id}")
async def api_delete_entity(entity_type: str, entity_id: int, session: Session = Depends(get_db_session)):
    try:
        success = await delete_entity(session, entity_type, entity_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entity not found")
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
