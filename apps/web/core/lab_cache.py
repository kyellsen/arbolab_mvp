from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from uuid import UUID

from arbolab.config import DEFAULT_CONFIG_FILENAME
from arbolab.core.security import LabRole
from arbolab.lab import Lab

from apps.web.core.paths import ensure_workspace_paths, resolve_workspace_paths


@dataclass
class _LabEntry:
    lab: Lab
    last_used: datetime
    config_mtime: float | None


class LabCache:
    def __init__(self, max_size: int = 8, ttl_seconds: int = 900) -> None:
        self._max_size = max_size
        self._ttl = timedelta(seconds=ttl_seconds)
        self._entries: dict[tuple[UUID, LabRole], _LabEntry] = {}
        self._lock = Lock()

    def get(self, workspace_id: UUID, role: LabRole) -> Lab:
        now = datetime.utcnow()
        key = (workspace_id, role)

        with self._lock:
            self._evict_expired(now)
            entry = self._entries.get(key)
            if entry and not self._config_changed(entry, workspace_id):
                entry.last_used = now
                return entry.lab

            if entry:
                self._evict_key(key)

            lab, config_mtime = self._create_lab(workspace_id, role)
            self._entries[key] = _LabEntry(lab=lab, last_used=now, config_mtime=config_mtime)
            self._evict_lru_if_needed()
            return lab

    def invalidate(self, workspace_id: UUID) -> None:
        with self._lock:
            keys = [key for key in self._entries if key[0] == workspace_id]
            for key in keys:
                self._evict_key(key)

    def _create_lab(self, workspace_id: UUID, role: LabRole) -> tuple[Lab, float | None]:
        paths = resolve_workspace_paths(workspace_id)
        ensure_workspace_paths(paths)
        lab = Lab.open(
            workspace_root=paths.workspace_root,
            input_root=paths.input_root,
            results_root=paths.results_root,
            role=role,
        )
        config_path = paths.workspace_root / DEFAULT_CONFIG_FILENAME
        config_mtime = config_path.stat().st_mtime if config_path.exists() else None
        return lab, config_mtime

    def _evict_expired(self, now: datetime) -> None:
        expired_keys = [
            key for key, entry in self._entries.items()
            if now - entry.last_used > self._ttl
        ]
        for key in expired_keys:
            self._evict_key(key)

    def _evict_lru_if_needed(self) -> None:
        while len(self._entries) > self._max_size:
            oldest_key = min(self._entries, key=lambda k: self._entries[k].last_used)
            self._evict_key(oldest_key)

    def _config_changed(self, entry: _LabEntry, workspace_id: UUID) -> bool:
        paths = resolve_workspace_paths(workspace_id)
        config_path = paths.workspace_root / DEFAULT_CONFIG_FILENAME
        if not config_path.exists():
            return entry.config_mtime is not None
        current_mtime = config_path.stat().st_mtime
        if entry.config_mtime is None:
            return True
        return current_mtime > entry.config_mtime

    def _evict_key(self, key: tuple[UUID, LabRole]) -> None:
        entry = self._entries.pop(key, None)
        if not entry:
            return
        try:
            engine = getattr(entry.lab.database, "_engine", None)
            if engine is not None:
                engine.dispose()
        except Exception:
            pass


_LAB_CACHE = LabCache()


def get_cached_lab(workspace_id: UUID, role: LabRole) -> Lab:
    return _LAB_CACHE.get(workspace_id, role)


def invalidate_cached_lab(workspace_id: UUID) -> None:
    _LAB_CACHE.invalidate(workspace_id)
