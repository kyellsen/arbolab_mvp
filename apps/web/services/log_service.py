"""Log service for collecting logs from different sources."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from apps.web.core.log_config import log_flags


class LogEntry(BaseModel):
    """A single log entry for the log drawer."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    level: Literal["debug", "info", "warn", "error"] = "info"
    source: Literal["frontend", "recipe", "system"] = "system"
    action: str | None = None  # e.g., "recipe_started", "entity_created"
    entity: str | None = None  # e.g., "Tree", "SensorCalibration"
    message: str = ""


# In-memory buffer for frontend logs (per workspace)
_frontend_logs: dict[str, list[LogEntry]] = {}


class LogService:
    """Collects logs from different sources for the log drawer."""
    
    @staticmethod
    def get_feature_flags() -> dict:
        """Return current feature flags for frontend config."""
        return {
            "frontendEnabled": log_flags.LOG_FRONTEND_ENABLED,
            "recipeEnabled": log_flags.LOG_RECIPE_ENABLED,
            "systemEnabled": log_flags.LOG_SYSTEM_ENABLED,
            "pollIntervalMs": log_flags.LOG_POLL_INTERVAL_MS,
            "maxEntries": log_flags.LOG_MAX_ENTRIES,
        }
    
    @staticmethod
    def add_frontend_log(workspace_id: str, entry: LogEntry) -> None:
        """Add a frontend log entry to the in-memory buffer."""
        if not log_flags.LOG_FRONTEND_ENABLED:
            return
        
        if workspace_id not in _frontend_logs:
            _frontend_logs[workspace_id] = []
        
        entry.source = "frontend"
        _frontend_logs[workspace_id].append(entry)
        
        # Keep only last N entries
        max_entries = log_flags.LOG_MAX_ENTRIES
        if len(_frontend_logs[workspace_id]) > max_entries:
            _frontend_logs[workspace_id] = _frontend_logs[workspace_id][-max_entries:]
    
    @staticmethod
    def get_frontend_logs(
        workspace_id: str,
        since: datetime | None = None
    ) -> list[LogEntry]:
        """Get frontend logs for a workspace, optionally filtered by timestamp."""
        if not log_flags.LOG_FRONTEND_ENABLED:
            return []
        
        logs = _frontend_logs.get(workspace_id, [])
        if since:
            logs = [log for log in logs if log.timestamp > since]
        return logs[-log_flags.LOG_MAX_ENTRIES:]
    
    @staticmethod
    def get_recipe_logs(
        workspace_root: Path,
        since: datetime | None = None
    ) -> list[LogEntry]:
        """Read recent recipe steps from the workspace recipe file."""
        if not log_flags.LOG_RECIPE_ENABLED:
            return []
        
        recipe_path = workspace_root / "recipes" / "current.json"
        print(f"[LogService] Looking for recipe at: {recipe_path}")
        print(f"[LogService] Recipe file exists: {recipe_path.exists()}")
        
        if not recipe_path.exists():
            # Return a placeholder log so user knows no recipes yet
            return [LogEntry(
                level="info",
                source="recipe",
                action="info",
                message=f"No recipe file yet at {recipe_path}"
            )]
        
        try:
            with open(recipe_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"[LogService] Loaded recipe with {len(data.get('steps', []))} steps")
        except (json.JSONDecodeError, IOError) as e:
            print(f"[LogService] Error loading recipe: {e}")
            return []
        
        entries = []
        for step in data.get("steps", []):
            step_time = step.get("timestamp")
            if step_time:
                if isinstance(step_time, str):
                    step_time = datetime.fromisoformat(step_time)
                
                if since and step_time <= since:
                    continue
            else:
                step_time = datetime.now()
            
            entries.append(LogEntry(
                timestamp=step_time,
                level="info",
                source="recipe",
                action=step.get("step_type", "unknown"),
                entity=step.get("params", {}).get("entity_type"),
                message=f"Recipe step: {step.get('step_type', 'unknown')}"
            ))
        
        # Return most recent first, limited
        return list(reversed(entries[-log_flags.LOG_MAX_ENTRIES:]))
    
    @staticmethod
    def get_system_logs(
        workspace_root: Path,
        since: datetime | None = None
    ) -> list[LogEntry]:
        """Read from workspace system log file with sanitization."""
        if not log_flags.LOG_SYSTEM_ENABLED:
            return []
        
        log_path = workspace_root / "logs" / "system.log"
        if not log_path.exists():
            return []
        
        entries = []
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except IOError:
            return []
        
        # Parse log lines (expected format from arbolab-logger file handler)
        # Format: "2026-01-08 20:00:00 [INFO] arbolab: message"
        for line in lines[-log_flags.LOG_MAX_ENTRIES:]:
            line = line.strip()
            if not line:
                continue
            
            entry = LogService._parse_log_line(line, workspace_root)
            if entry:
                if since and entry.timestamp <= since:
                    continue
                entries.append(entry)
        
        return list(reversed(entries))
    
    @staticmethod
    def _parse_log_line(line: str, workspace_root: Path) -> LogEntry | None:
        """Parse a log line into a LogEntry with sanitization."""
        # Expected format: "2026-01-08 20:00:00 [LEVEL] name: message"
        try:
            # Simple parsing - adapt to actual arbolab-logger format
            parts = line.split(" ", 3)
            if len(parts) < 4:
                return LogEntry(
                    level="info",
                    source="system", 
                    message=line[:200]  # Truncate long messages
                )
            
            date_str = f"{parts[0]} {parts[1]}"
            level_str = parts[2].strip("[]").lower()
            message = parts[3] if len(parts) > 3 else ""
            
            # Sanitize: Replace absolute paths with relative
            workspace_str = str(workspace_root)
            if workspace_str in message:
                message = message.replace(workspace_str, "./")
            
            # Map level
            level_map = {"debug": "debug", "info": "info", "warning": "warn", "error": "error"}
            level = level_map.get(level_str, "info")
            
            return LogEntry(
                timestamp=datetime.fromisoformat(date_str.replace("[", "").replace("]", "")),
                level=level,
                source="system",
                message=message[:500]  # Limit message length
            )
        except (ValueError, IndexError):
            return LogEntry(
                level="info",
                source="system",
                message=line[:200]
            )
    
    @staticmethod
    def get_all_logs(
        workspace_id: str,
        workspace_root: Path,
        tab: Literal["frontend", "recipe", "system"] | None = None,
        since: datetime | None = None
    ) -> list[LogEntry]:
        """Get logs from all sources or a specific tab."""
        logs: list[LogEntry] = []
        
        if tab is None or tab == "frontend":
            logs.extend(LogService.get_frontend_logs(workspace_id, since))
        
        if tab is None or tab == "recipe":
            logs.extend(LogService.get_recipe_logs(workspace_root, since))
        
        if tab is None or tab == "system":
            logs.extend(LogService.get_system_logs(workspace_root, since))
        
        # Sort by timestamp descending (most recent first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return logs[:log_flags.LOG_MAX_ENTRIES]
