import os
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from apps.web.core.database import get_session
from apps.web.core.plugin_nav import (
    build_plugin_nav_items,
    get_enabled_plugins,
    get_plugin_description,
    get_plugin_label,
)
from apps.web.models.auth import UserWorkspaceAssociation, Workspace
from apps.web.models.user import User
from apps.web.routers.api import get_current_user_id, get_current_workspace

router = APIRouter(prefix="/plugins", tags=["plugins"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@router.get("/{plugin_id}", response_class=HTMLResponse)
async def plugin_page(
    request: Request,
    plugin_id: str,
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

    enabled_plugins = get_enabled_plugins(current_workspace.id)
    if plugin_id not in enabled_plugins:
        raise HTTPException(status_code=404, detail="Plugin not enabled")

    plugin_nav = build_plugin_nav_items(enabled_plugins)
    plugin = {
        "id": plugin_id,
        "label": get_plugin_label(plugin_id),
        "description": get_plugin_description(plugin_id),
    }

    context = {
        "request": request,
        "user": user,
        "current_workspace": current_workspace,
        "all_workspaces": all_workspaces,
        "plugin_nav": plugin_nav,
        "plugin": plugin,
    }

    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
        return templates.TemplateResponse("partials/plugin_content.html", context)

    return templates.TemplateResponse("plugins/plugin.html", context)
