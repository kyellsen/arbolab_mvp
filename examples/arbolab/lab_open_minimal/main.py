"""
Minimal Lab Example

Usage:
  This script relies on the 'arbolab' and 'arbolab-logger' packages in the workspace.
  You must run it within the configured environment using `uv run` or by ensuring PYTHONPATH is set.

  Command:
    uv run python examples/arbolab/lab_open_minimal/main.py
"""
import shutil
from pathlib import Path

from arbolab.lab import Lab
from arbolab_logger import LoggerConfig, configure_logger, get_logger

# 1. Setup Logging (Global Config for the runtime)
configure_logger(LoggerConfig(
    level="DEBUG", 
    colorize=True,
    # Arbolab automatically handles file logging to workspace/logs/
))

def main():
    # Define roots
    base_root = Path("examples/arbolab/lab_open_minimal/example_workspace").resolve()
    input_root = base_root / "input"
    workspace_root = base_root / "workspace"
    results_root = base_root / "results"

    # Cleanup for clean run (Persist Input!)
    if workspace_root.exists():
        shutil.rmtree(workspace_root)
    if results_root.exists():
        shutil.rmtree(results_root)
    
    # Ensure input exists (part of repo usually, but ensure here)
    input_root.mkdir(parents=True, exist_ok=True)
    
    # 2. Open Lab
    lab = Lab.open(
        workspace_root=None, # Must be None if base_root is used
        base_root=base_root
    )

    # 3. Domain Operation (Create Project)
    # Using the Recipe-aware method instead of direct session.add()
    project = lab.define_project(name="My First Project", description="Created via minimal example")
        
    # 4. Re-open Lab (Persistence Check)
    lab_reopened = Lab.open(workspace_root=workspace_root)
    
    if str(lab_reopened.input_root) != str(input_root.resolve()):
         raise RuntimeError(f"Failed to restore Input Root! Got: {lab_reopened.input_root}, Expected: {input_root.resolve()}")

if __name__ == "__main__":
    main()
