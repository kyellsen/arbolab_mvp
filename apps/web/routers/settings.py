import os
from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path

from apps.web.core.database import get_session
from apps.web.models.user import User
from apps.web.models.auth import Workspace, UserWorkspaceAssociation
from apps.web.core.security import get_password_hash, verify_password
from apps.web.routers.api import get_current_user_id, get_current_workspace
from apps.web.core.lab_cache import invalidate_cached_lab
from apps.web.core.paths import resolve_workspace_paths, ensure_workspace_paths
from arbolab.config import load_config, update_config

router = APIRouter(prefix="/settings", tags=["settings"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def _is_hx_target(request: Request, target: str) -> bool:
    return request.headers.get("HX-Request") and request.headers.get("HX-Target") == target

def _get_user_workspace_context(request: Request, user_id: UUID, session: Session):
    user = session.get(User, user_id)
    if not user:
        return None, None, []

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
        try:
            active_uuid = UUID(active_ws_id)
        except (ValueError, TypeError):
            active_uuid = None

        if active_uuid:
            for workspace in all_workspaces:
                if workspace.id == active_uuid:
                    current_workspace = workspace
                    break

    if not current_workspace and user.last_active_workspace_id:
        for workspace in all_workspaces:
            if workspace.id == user.last_active_workspace_id:
                current_workspace = workspace
                break

    if not current_workspace and all_workspaces:
        current_workspace = all_workspaces[0]

    if current_workspace:
        request.session["active_workspace_id"] = str(current_workspace.id)
        if user.last_active_workspace_id != current_workspace.id:
            user.last_active_workspace_id = current_workspace.id
            session.add(user)
            session.commit()

    return user, current_workspace, all_workspaces

def _load_workspace_config(current_workspace: Workspace):
    paths = resolve_workspace_paths(current_workspace.id)
    ensure_workspace_paths(paths)
    return load_config(paths.workspace_root)

@router.get("/", response_class=HTMLResponse)
async def settings_index(
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    user, current_workspace, all_workspaces = _get_user_workspace_context(request, user_id, session)
    if not user:
        return RedirectResponse(url="/auth/login")

    context = {
        "request": request,
        "user": user,
        "current_workspace": current_workspace,
        "all_workspaces": all_workspaces,
        "active_tab": "profile"
    }

    if _is_hx_target(request, "settings-content"):
        return templates.TemplateResponse("settings/partials/profile_form.html", context)

    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
        return templates.TemplateResponse("settings/partials/user_settings_content.html", context)

    return templates.TemplateResponse("settings/settings_layout.html", context)

@router.put("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    full_name: Annotated[str | None, Form()] = None,
    organization: Annotated[str | None, Form()] = None,
    address_line1: Annotated[str | None, Form()] = None,
    address_line2: Annotated[str | None, Form()] = None,
    city: Annotated[str | None, Form()] = None,
    zip_code: Annotated[str | None, Form()] = None,
    country: Annotated[str | None, Form()] = None,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    def normalize_text(value: str | None) -> tuple[bool, str | None]:
        """Normalize optional text fields and signal whether the input was provided."""
        if value is None:
            return False, None
        normalized = value.strip()
        return True, normalized if normalized else None

    updates = {
        "full_name": full_name,
        "organization": organization,
        "address_line1": address_line1,
        "address_line2": address_line2,
        "city": city,
        "zip_code": zip_code,
        "country": country,
    }
    for field_name, raw_value in updates.items():
        provided, cleaned = normalize_text(raw_value)
        if provided:
            setattr(user, field_name, cleaned)
    
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
    user, current_workspace, all_workspaces = _get_user_workspace_context(request, user_id, session)
    if not user:
        return RedirectResponse(url="/auth/login")

    context = {
        "request": request,
        "user": user,
        "current_workspace": current_workspace,
        "all_workspaces": all_workspaces,
        "active_tab": "security"
    }

    if _is_hx_target(request, "settings-content"):
        return templates.TemplateResponse("settings/partials/security_form.html", context)

    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
        return templates.TemplateResponse("settings/partials/user_settings_content.html", context)

    return templates.TemplateResponse("settings/settings_layout.html", context)

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

@router.get("/lab", response_class=HTMLResponse)
async def lab_settings_page(
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
    current_workspace: Workspace = Depends(get_current_workspace),
):
    user = session.get(User, user_id)
    if not user:
        return RedirectResponse(url="/auth/login")

    stmt = (
        select(Workspace)
        .join(UserWorkspaceAssociation)
        .where(UserWorkspaceAssociation.user_id == user_id)
        .order_by(Workspace.created_at)
    )
    all_workspaces = session.exec(stmt).all()

    config = _load_workspace_config(current_workspace)

    context = {
        "request": request,
        "user": user,
        "current_workspace": current_workspace,
        "all_workspaces": all_workspaces,
        "config": config,
        "workspace": current_workspace
    }

    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
        return templates.TemplateResponse("settings/partials/lab_settings_content.html", context)

    return templates.TemplateResponse("settings/lab_settings.html", context)

@router.get("/lab/config", response_class=HTMLResponse)
async def lab_config_tab(
    request: Request,
    current_workspace: Workspace = Depends(get_current_workspace),
):
    config = _load_workspace_config(current_workspace)

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
    ensure_workspace_paths(paths)

    update_config(paths.workspace_root, updates)
    config = load_config(paths.workspace_root)
    invalidate_cached_lab(current_workspace.id)
    
    response = templates.TemplateResponse("settings/partials/lab_config.html", {
        "request": request,
        "config": config,
        "workspace": current_workspace,
        "success": "Lab configuration saved"
    })
    response.headers["HX-Trigger"] = '{"show-toast": "Lab config saved"}'
    return response
