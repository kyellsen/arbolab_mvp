from __future__ import annotations

from uuid import UUID

from arbolab.config import load_config

from apps.web.core.paths import ensure_workspace_paths, resolve_workspace_paths

PLUGIN_LABELS: dict[str, str] = {
    "ls3": "LineScale v3",
    "ptq": "TreeQinetic",
    "mock_plugin": "Mock Plugin",
}

PLUGIN_DESCRIPTIONS: dict[str, str] = {
    "ls3": "LineScale v3 plugin workspace placeholder.",
    "ptq": "TreeQinetic plugin workspace placeholder.",
    "mock_plugin": "Mock plugin workspace placeholder.",
}


def get_enabled_plugins(workspace_id: UUID | None) -> list[str]:
    if not workspace_id:
        return []
    try:
        paths = resolve_workspace_paths(workspace_id)
    except ValueError:
        return []
    ensure_workspace_paths(paths)
    config = load_config(paths.workspace_root)
    return list(config.enabled_plugins or [])


def get_plugin_label(plugin_id: str) -> str:
    if plugin_id in PLUGIN_LABELS:
        return PLUGIN_LABELS[plugin_id]
    return plugin_id.replace("_", " ").upper()


def get_plugin_description(plugin_id: str) -> str:
    if plugin_id in PLUGIN_DESCRIPTIONS:
        return PLUGIN_DESCRIPTIONS[plugin_id]
    return "Plugin workspace placeholder."


def build_plugin_nav_items(plugin_ids: list[str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for plugin_id in plugin_ids:
        items.append(
            {
                "id": plugin_id,
                "label": get_plugin_label(plugin_id),
                "description": get_plugin_description(plugin_id),
            }
        )
    return items
