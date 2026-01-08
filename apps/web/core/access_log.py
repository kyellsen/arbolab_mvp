"""Middleware for mirroring backend access logs into workspace system.log."""

from __future__ import annotations

from datetime import datetime
from time import monotonic
from uuid import UUID

from fastapi import Request

from apps.web.core.paths import resolve_workspace_paths


def _format_access_message(request: Request, status_code: int, duration_ms: float) -> str:
    client = request.client.host if request.client else "-"
    path = request.url.path
    if request.url.query:
        path = f"{path}?{request.url.query}"
    return f'{client} "{request.method} {path}" {status_code} {duration_ms:.1f}ms'


def _level_for_status(status_code: int) -> str:
    if status_code >= 500:
        return "ERROR"
    if status_code >= 400:
        return "WARNING"
    return "INFO"


def _write_access_log(workspace_id: str, line: str) -> None:
    try:
        workspace_uuid = UUID(workspace_id)
    except (ValueError, TypeError):
        return
    try:
        paths = resolve_workspace_paths(workspace_uuid)
        log_path = paths.workspace_root / "logs" / "system.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except (OSError, ValueError):
        return


async def access_log_middleware(request: Request, call_next):
    start = monotonic()
    response = await call_next(request)

    workspace_id = getattr(request.state, "workspace_id", None)
    if workspace_id is None:
        try:
            workspace_id = request.session.get("active_workspace_id")
        except Exception:
            workspace_id = None

    if workspace_id:
        duration_ms = (monotonic() - start) * 1000.0
        level = _level_for_status(response.status_code)
        message = _format_access_message(request, response.status_code, duration_ms)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} [{level}] web.access: {message}"
        _write_access_log(str(workspace_id), line)

    return response
