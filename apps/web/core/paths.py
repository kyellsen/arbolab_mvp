from pathlib import Path
from uuid import UUID

from apps.web.core.config import load_web_config


class LabPaths:
    def __init__(self, workspace_root: Path, input_root: Path, results_root: Path):
        self.workspace_root = workspace_root
        self.input_root = input_root
        self.results_root = results_root

def resolve_workspace_paths(workspace_id: UUID) -> LabPaths:
    """
    Generates isolated paths for a specific Workspace.
    Structure: {DATA_ROOT}/workspaces/{workspace_id}/...
    """
    config = load_web_config()
    
    # Ensure data_root is absolute
    safe_root = config.data_root.resolve()
    
    # Construct base path for this specific workspace
    # Flattened: /data/workspaces/{uuid}
    base = safe_root / "workspaces" / str(workspace_id)
    final_base = base.resolve()
    
    # Security: Ensure we haven't traversed out of safe_root
    if safe_root not in final_base.parents and safe_root != final_base:
         raise ValueError(f"Security violation: Path {final_base} is outside data root {safe_root}")

    return LabPaths(
        workspace_root=final_base / "workspace",
        input_root=final_base / "input",
        results_root=final_base / "results"
    )

def ensure_workspace_paths(paths: LabPaths):
    """Physically creates the directory structure."""
    paths.workspace_root.mkdir(parents=True, exist_ok=True)
    paths.input_root.mkdir(parents=True, exist_ok=True)
    paths.results_root.mkdir(parents=True, exist_ok=True)
