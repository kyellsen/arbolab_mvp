import os
from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path

from apps.web.core.database import get_session, SessionDep
from apps.web.models.user import User
from apps.web.models.auth import Workspace, UserWorkspaceAssociation
from apps.web.core.security import get_password_hash, verify_password
from apps.web.routers.api import get_current_user_id, get_current_workspace
from arbolab.lab import Lab
from apps.web.core.paths import resolve_workspace_paths, ensure_workspace_paths

router = APIRouter(prefix="/settings", tags=["settings"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/", response_class=HTMLResponse)
async def settings_index(
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        return RedirectResponse(url="/auth/login")
    
    # Get Workspaces for sidebar context
    stmt = (
        select(Workspace)
        .join(UserWorkspaceAssociation)
        .where(UserWorkspaceAssociation.user_id == user_id)
        .order_by(Workspace.created_at)
    )
    all_workspaces = session.exec(stmt).all()
    
    active_ws_id = request.session.get("active_workspace_id")
    current_workspace = None
    if active_ws_id:
        current_workspace = session.get(Workspace, UUID(active_ws_id))

    context = {
        "request": request,
        "user": user,
        "current_workspace": current_workspace,
        "all_workspaces": all_workspaces,
        "active_tab": "profile"
    }
    
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("settings/partials/profile_form.html", context)
    
    return templates.TemplateResponse("settings/settings_layout.html", context)

@router.put("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    full_name: Annotated[str, Form()],
    organization: Annotated[str, Form()],
    address_line1: Annotated[str, Form()],
    address_line2: Annotated[str, Form()] = None,
    city: Annotated[str, Form()] = None,
    zip_code: Annotated[str, Form()] = None,
    country: Annotated[str, Form()] = None,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.full_name = full_name
    user.organization = organization
    user.address_line1 = address_line1
    user.address_line2 = address_line2
    user.city = city
    user.zip_code = zip_code
    user.country = country
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    response = templates.TemplateResponse("settings/partials/profile_form.html", {
        "request": request,
        "user": user,
        "success": "Profile updated successfully"
    })
    response.headers["HX-Trigger"] = '{"show-toast": "Profile saved"}'
    return response

@router.get("/security", response_class=HTMLResponse)
async def security_tab(request: Request, user_id: UUID = Depends(get_current_user_id), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return templates.TemplateResponse("settings/partials/security_form.html", {"request": request, "user": user})

@router.put("/password", response_class=HTMLResponse)
async def update_password(
    request: Request,
    current_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    
    if not verify_password(current_password, user.hashed_password):
        return templates.TemplateResponse("settings/partials/security_form.html", {
            "request": request,
            "user": user,
            "error": "Current password incorrect"
        })
    
    if new_password != confirm_password:
        return templates.TemplateResponse("settings/partials/security_form.html", {
            "request": request,
            "user": user,
            "error": "New passwords do not match"
        })
    
    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    session.commit()
    
    response = templates.TemplateResponse("settings/partials/security_form.html", {
        "request": request,
        "user": user,
        "success": "Password updated successfully"
    })
    response.headers["HX-Trigger"] = '{"show-toast": "Password updated"}'
    return response

@router.delete("/account", response_class=HTMLResponse)
async def delete_account(
    request: Request,
    confirmation: Annotated[str, Form()],
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    if confirmation != "DELETE":
        user = session.get(User, user_id)
        return templates.TemplateResponse("settings/partials/security_form.html", {
            "request": request,
            "user": user,
            "error": "Please type DELETE to confirm"
        })
    
    user = session.get(User, user_id)
    # The requirement says "Deletes the user and their owned workspaces (Cascade)"
    # SQLModel/SQLAlchemy relationships should handle cascade if configured, 
    # but we should ensure it.
    
    session.delete(user)
    session.commit()
    
    request.session.clear()
    return HTMLResponse(content="", headers={"HX-Redirect": "/auth/login"})

@router.get("/lab/config", response_class=HTMLResponse)
async def lab_config_tab(
    request: Request,
    current_workspace: Workspace = Depends(get_current_workspace),
):
    # Read config.yaml
    paths = resolve_workspace_paths(current_workspace.id)
    ensure_workspace_paths(paths)
    
    from arbolab.config import load_config
    config = load_config(paths.workspace_root)
    
    return templates.TemplateResponse("settings/partials/lab_config.html", {
        "request": request,
        "config": config,
        "workspace": current_workspace
    })

@router.put("/lab/config", response_class=HTMLResponse)
async def update_lab_config(
    request: Request,
    current_workspace: Workspace = Depends(get_current_workspace),
    # We'll handle generic form fields from the partial
):
    form_data = await request.form()
    updates = {}
    
    # Define safe keys
    SAFE_KEYS = ["input_path", "results_path", "enabled_plugins"]
    
    for key in SAFE_KEYS:
        if key in form_data:
            if key == "enabled_plugins":
                # Handle list if multiple
                updates[key] = form_data.getlist(key)
            else:
                updates[key] = form_data[key]
    
    paths = resolve_workspace_paths(current_workspace.id)
    
    from arbolab.config import load_config
    import yaml
    
    # Custom helper function we'll add to config.py later or implement here
    config_path = paths.workspace_root / "config.yaml"
    
    if config_path.exists():
        with open(config_path, "r") as f:
            full_config = yaml.safe_load(f) or {}
    else:
        full_config = {}
        
    full_config.update(updates)
    
    with open(config_path, "w") as f:
        yaml.safe_dump(full_config, f, sort_keys=False)
        
    config = load_config(paths.workspace_root)
    
    response = templates.TemplateResponse("settings/partials/lab_config.html", {
        "request": request,
        "config": config,
        "workspace": current_workspace,
        "success": "Lab configuration saved"
    })
    response.headers["HX-Trigger"] = '{"show-toast": "Lab config saved"}'
    return response
