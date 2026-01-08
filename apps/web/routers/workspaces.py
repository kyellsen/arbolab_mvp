from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from apps.web.core.database import get_session
from apps.web.models.auth import User, Workspace
from apps.web.routers.api import get_current_user_id

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.get("/")
async def list_workspaces(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[Session, Depends(get_session)]
):
    """List all workspaces for the current user."""
    stmt = select(Workspace).where(Workspace.owner_id == user_id).order_by(Workspace.created_at)
    workspaces = session.exec(stmt).all()
    return workspaces

@router.post("/activate")
async def activate_workspace(
    request: Request,
    workspace_id: str, # Form data or JSON
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[Session, Depends(get_session)]
):
    """Sets the active workspace in the session."""
    # Verify ownership
    try:
        w_uuid = UUID(workspace_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    stmt = select(Workspace).where(Workspace.id == w_uuid, Workspace.owner_id == user_id)
    workspace = session.exec(stmt).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
    
    # Update Session
    request.session["active_workspace_id"] = str(workspace.id)
    
    return {"status": "activated", "workspace": workspace.name}
