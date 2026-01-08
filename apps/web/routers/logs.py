"""API router for log drawer endpoints."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from apps.web.core.paths import resolve_workspace_paths
from apps.web.models.auth import Workspace
from apps.web.routers.api import get_current_workspace
from apps.web.services.log_service import LogEntry, LogService

router = APIRouter(prefix="/api/logs", tags=["logs"])


class LogResponse(BaseModel):
    """Response model for log endpoint."""
    logs: list[LogEntry]
    feature_flags: dict
    timestamp: datetime


class FrontendLogRequest(BaseModel):
    """Request model for posting frontend logs."""
    level: Literal["debug", "info", "warn", "error"] = "info"
    message: str
    action: str | None = None


@router.get("")
async def get_logs(
    request: Request,
    tab: Literal["frontend", "recipe", "system"] | None = None,
    since: str | None = None,
    workspace: Workspace = Depends(get_current_workspace),
) -> LogResponse:
    """
    Returns recent logs for the specified tab, filtered by workspace.
    
    Query params:
    - tab: "frontend", "recipe", or "system". None returns all enabled tabs.
    - since: ISO timestamp to filter logs after this time.
    """
    workspace_id = str(workspace.id)
    paths = resolve_workspace_paths(workspace.id)
    
    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            pass
    
    logs = LogService.get_all_logs(
        workspace_id=workspace_id,
        workspace_root=paths.workspace_root,
        tab=tab,
        since=since_dt
    )
    
    return LogResponse(
        logs=logs,
        feature_flags=LogService.get_feature_flags(),
        timestamp=datetime.now()
    )


@router.post("/frontend")
async def post_frontend_log(
    data: FrontendLogRequest,
    workspace: Workspace = Depends(get_current_workspace),
) -> dict:
    """
    Receives a frontend log entry from the browser.
    Used to capture JS errors or explicit logging calls.
    """
    workspace_id = str(workspace.id)
    
    entry = LogEntry(
        level=data.level,
        source="frontend",
        action=data.action,
        message=data.message
    )
    
    LogService.add_frontend_log(workspace_id, entry)
    
    return {"status": "ok"}


@router.get("/config")
async def get_log_config() -> dict:
    """Returns log feature flags for frontend configuration."""
    return LogService.get_feature_flags()
