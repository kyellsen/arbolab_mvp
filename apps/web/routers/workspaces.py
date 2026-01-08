from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from apps.web.core.database import get_session
from apps.web.routers.api import get_current_user_id
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from fastapi import Form
from apps.web.models.auth import Workspace, UserWorkspaceAssociation
from apps.web.models.user import User
from arbolab.core.security import LabRole
# Use BASE_DIR from main (circular import avoidance or re-calculate)
# Better: simpler import or just use relative path if known structure
import os

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

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

@router.get("/new", response_class=HTMLResponse)
async def new_workspace_page(request: Request):
    user = request.session.get("user")
    if not user:
         return RedirectResponse(url="/auth/login")
    return templates.TemplateResponse("workspaces/new.html", {"request": request})

@router.post("/")
async def create_workspace(
    request: Request,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[Session, Depends(get_session)],
    name: str = Form(...),
):
    """Creates a new workspace and sets it as active."""
    # 1. Create Workspace
    workspace = Workspace(name=name, owner_id=user_id)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    
    # 2. Create Association (Admin)
    association = UserWorkspaceAssociation(
        user_id=user_id,
        workspace_id=workspace.id,
        role=LabRole.ADMIN
    )
    session.add(association)
    session.commit()
    
    # 3. Set Active Session
    request.session["active_workspace_id"] = str(workspace.id)
    
    # 4. Redirect to Dashboard
    return RedirectResponse(url="/", status_code=303)
