import logging
import os
import shutil
from pathlib import Path
from typing import Annotated
from uuid import UUID

from arbolab.config import load_config
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from apps.web.core.database import get_session
from apps.web.core.lab_cache import invalidate_cached_lab
from apps.web.core.paths import ensure_workspace_paths, resolve_workspace_paths
from apps.web.core.plugin_nav import build_plugin_nav_items, get_enabled_plugins
from apps.web.core.security import get_password_hash, verify_password
from apps.web.models.auth import UserWorkspaceAssociation, Workspace
from apps.web.models.user import User
from apps.web.routers.api import get_current_user_id, get_current_workspace, get_lab

router = APIRouter(prefix="/settings", tags=["settings"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
logger = logging.getLogger(__name__)

def _is_hx_target(request: Request, target: str) -> bool:
    return request.headers.get("HX-Request") and request.headers.get("HX-Target") == target

def _get_user_workspace_ids(session: Session, user_id: UUID) -> list[UUID]:
    """Return workspace IDs associated with a user.

    Args:
        session: Active database session.
        user_id: User identifier.

    Returns:
        Workspace IDs linked to the user.
    """
    stmt = select(UserWorkspaceAssociation.workspace_id).where(
        UserWorkspaceAssociation.user_id == user_id
    )
    return list(session.exec(stmt).all())

def _get_orphaned_workspace_ids(session: Session, user_id: UUID, workspace_ids: list[UUID]) -> list[UUID]:
    """Return workspace IDs that are only associated with the given user.

    Args:
        session: Active database session.
        user_id: User identifier to check for exclusivity.
        workspace_ids: Workspace IDs linked to the user.

    Returns:
        Workspace IDs that have no other associated users.
    """
    orphaned_ids: list[UUID] = []
    for workspace_id in workspace_ids:
        assoc_stmt = select(UserWorkspaceAssociation.user_id).where(
            UserWorkspaceAssociation.workspace_id == workspace_id
        )
        assoc_user_ids = session.exec(assoc_stmt).all()
        if assoc_user_ids and all(assoc_user_id == user_id for assoc_user_id in assoc_user_ids):
            orphaned_ids.append(workspace_id)
    return orphaned_ids

def _delete_workspace_storage(workspace_id: UUID) -> None:
    """Delete workspace storage directories for a workspace ID.

    Args:
        workspace_id: Workspace identifier.
    """
    paths = resolve_workspace_paths(workspace_id)
    base_dir = paths.workspace_root.parent
    if not base_dir.exists():
        return
    shutil.rmtree(base_dir)

def _delete_user_and_orphaned_workspaces(session: Session, user_id: UUID) -> list[UUID]:
    """Delete user, their associations, and orphaned workspaces.

    Args:
        session: Active database session.
        user_id: User identifier to delete.

    Returns:
        Workspace IDs that should have storage deleted.
    """
    workspace_ids = _get_user_workspace_ids(session, user_id)
    orphaned_workspace_ids = _get_orphaned_workspace_ids(session, user_id, workspace_ids)

    assoc_rows = session.exec(
        select(UserWorkspaceAssociation).where(UserWorkspaceAssociation.user_id == user_id)
    ).all()
    for assoc in assoc_rows:
        session.delete(assoc)

    if orphaned_workspace_ids:
        workspaces = session.exec(
            select(Workspace).where(Workspace.id.in_(orphaned_workspace_ids))
        ).all()
        for workspace in workspaces:
            session.delete(workspace)

    user = session.get(User, user_id)
    if user:
        session.delete(user)

    return orphaned_workspace_ids

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


def _build_plugin_nav(current_workspace: Workspace | None) -> list[dict[str, str]]:
    if not current_workspace:
        return []
    return build_plugin_nav_items(get_enabled_plugins(current_workspace.id))

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
        "active_tab": "profile",
        "plugin_nav": _build_plugin_nav(current_workspace),
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
    utc_offset_sign: Annotated[str | None, Form()] = None,
    utc_offset_hours: Annotated[str | None, Form()] = None,
    utc_offset_minutes: Annotated[str | None, Form()] = None,
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

    def parse_utc_offset(
        sign: str | None,
        hours: str | None,
        minutes: str | None,
    ) -> int | None:
        """Parse manual UTC offset into minutes."""
        raw_hours = (hours or "").strip()
        raw_minutes = (minutes or "").strip()

        if not raw_hours and not raw_minutes:
            return None

        try:
            hours_value = int(raw_hours) if raw_hours else 0
            minutes_value = int(raw_minutes) if raw_minutes else 0
        except ValueError as exc:
            raise ValueError("UTC offset must use numeric hours and minutes.") from exc

        if hours_value < 0 or minutes_value < 0:
            raise ValueError("UTC offset hours and minutes must be positive.")
        if hours_value > 14 or minutes_value > 59:
            raise ValueError("UTC offset must be within +/-14:00.")
        if hours_value == 14 and minutes_value > 0:
            raise ValueError("UTC offset must be within +/-14:00.")

        sign_value = -1 if sign == "-" else 1
        return sign_value * (hours_value * 60 + minutes_value)

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

    try:
        user.utc_offset_minutes = parse_utc_offset(
            utc_offset_sign,
            utc_offset_hours,
            utc_offset_minutes,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            "settings/partials/profile_form.html",
            {
                "request": request,
                "user": user,
                "error": str(exc),
            },
            status_code=400,
        )
    
    session.add(user)
    session.commit()
    session.refresh(user)

    if request.session.get("user"):
        request.session["user"]["utc_offset_minutes"] = user.utc_offset_minutes
    
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
        "active_tab": "security",
        "plugin_nav": _build_plugin_nav(current_workspace),
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

@router.post("/account", response_class=HTMLResponse)
@router.delete("/account", response_class=HTMLResponse)
async def delete_account(
    request: Request,
    password: Annotated[str, Form()],
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        return RedirectResponse(url="/auth/login")

    if not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("settings/partials/security_form.html", {
            "request": request,
            "user": user,
            "error": "Current password incorrect"
        })

    orphaned_workspace_ids = _delete_user_and_orphaned_workspaces(session, user_id)
    session.commit()

    for workspace_id in orphaned_workspace_ids:
        invalidate_cached_lab(workspace_id)
        try:
            _delete_workspace_storage(workspace_id)
        except OSError as exc:
            logger.warning(
                "Failed to delete workspace storage for %s: %s",
                workspace_id,
                exc,
            )

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
        "workspace": current_workspace,
        "plugin_nav": _build_plugin_nav(current_workspace),
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
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    form_data = await request.form()
    updates = {}
    
    # Define safe keys
    SAFE_KEYS = ["input_path", "results_path", "enabled_plugins"]
    
    for key in SAFE_KEYS:
        if key == "enabled_plugins":
            # Always persist, even when empty, to allow disabling all plugins.
            updates[key] = form_data.getlist(key) if "enabled_plugins" in form_data else []
            continue
        if key in form_data:
            updates[key] = form_data[key]
    
    lab = get_lab(user_id=user_id, workspace=current_workspace, session=session)
    lab.modify_config(**updates)
    
    config = lab.config
    
    response = templates.TemplateResponse("settings/partials/lab_config.html", {
        "request": request,
        "config": config,
        "workspace": current_workspace,
        "success": "Lab configuration saved"
    })
    response.headers["HX-Trigger"] = '{"show-toast": "Lab config saved", "lab-config-updated": true}'
    return response
