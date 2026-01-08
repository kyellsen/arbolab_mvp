from pathlib import Path
from uuid import UUID
from arbolab.config import load_config

class LabPaths:
    def __init__(self, workspace_root: Path, input_root: Path, results_root: Path):
        self.workspace_root = workspace_root
        self.input_root = input_root
        self.results_root = results_root

def resolve_workspace_paths(user_id: UUID, workspace_id: UUID) -> LabPaths:
    """
    Generates isolated paths for a specific User and Workspace.
    Structure: {DATA_ROOT}/{user_id}/{workspace_id}/...
    """
    config = load_config()
    
    # Ensure data_root is absolute
    safe_root = config.data_root.resolve()
    
    # Construct base path for this specific workspace
    base = safe_root / str(user_id) / str(workspace_id)
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
