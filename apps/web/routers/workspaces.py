import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from apps.web.core.database import get_session
from apps.web.routers.api import get_current_user_id, get_current_user, get_current_workspace
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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
    stmt = (
        select(Workspace)
        .join(UserWorkspaceAssociation)
        .where(UserWorkspaceAssociation.user_id == user_id)
        .order_by(Workspace.created_at)
    )
    workspaces = session.exec(stmt).all()
    return workspaces

@router.post("/activate")
async def activate_workspace(
    request: Request,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[Session, Depends(get_session)],
    workspace_id: Annotated[str | None, Form()] = None
):
    """Sets the active workspace in the session."""
    if workspace_id is None:
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        workspace_id = payload.get("workspace_id")

    if not workspace_id:
        raise HTTPException(status_code=400, detail="Missing workspace_id")
    # Verify access via association
    try:
        w_uuid = UUID(workspace_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    stmt = (
        select(Workspace)
        .join(UserWorkspaceAssociation)
        .where(Workspace.id == w_uuid)
        .where(UserWorkspaceAssociation.user_id == user_id)
    )
    workspace = session.exec(stmt).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")
    
    # Update Session
    request.session["active_workspace_id"] = str(workspace.id)

    response = JSONResponse({"status": "activated", "workspace": workspace.name})
    response.headers["HX-Trigger"] = json.dumps({
        "workspace-activated": {
            "workspaceId": str(workspace.id),
            "workspaceName": workspace.name,
        }
    })
    return response


@router.get("/switcher", response_class=HTMLResponse)
async def workspace_switcher(
    request: Request,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[Session, Depends(get_session)],
    current_workspace: Workspace = Depends(get_current_workspace),
):
    stmt = (
        select(Workspace)
        .join(UserWorkspaceAssociation)
        .where(UserWorkspaceAssociation.user_id == user_id)
        .order_by(Workspace.created_at)
    )
    all_workspaces = session.exec(stmt).all()
    return templates.TemplateResponse("partials/workspace_switcher_content.html", {
        "request": request,
        "current_workspace": current_workspace,
        "all_workspaces": all_workspaces,
    })

@router.get("/new", response_class=HTMLResponse)
async def new_workspace_page(
    request: Request,
    session: Annotated[Session, Depends(get_session)]
):
    user = request.session.get("user")
    if not user:
         return RedirectResponse(url="/auth/login")
    
    # Check if user has any existing workspaces via association
    user_id = UUID(user.get("id"))
    stmt = (
        select(Workspace)
        .join(UserWorkspaceAssociation)
        .where(UserWorkspaceAssociation.user_id == user_id)
    )
    existing_workspaces = session.exec(stmt).all()
    is_first_lab = len(existing_workspaces) == 0
    
    return templates.TemplateResponse("workspaces/new.html", {
        "request": request,
        "user": user,
        "is_first_lab": is_first_lab
    })

@router.post("/")
async def create_workspace(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    name: str = Form(...),
):
    """Creates a new workspace and sets it as active."""
    # 1. Create Workspace (no owner_id anymore - uses association table)
    workspace = Workspace(name=name)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    
    # 2. Create Association (Admin)
    association = UserWorkspaceAssociation(
        user_id=current_user.id,
        workspace_id=workspace.id,
        role=LabRole.ADMIN
    )
    session.add(association)
    session.commit()
    
    # 3. Set Active Session
    request.session["active_workspace_id"] = str(workspace.id)
    
    # 4. Redirect to Dashboard
    return RedirectResponse(url="/", status_code=303)
