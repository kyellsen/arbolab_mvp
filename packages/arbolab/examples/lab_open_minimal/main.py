"""
Minimal Lab Example

Usage:
  This script relies on the 'arbolab' and 'arbolab-logger' packages in the workspace.
  You must run it within the configured environment using `uv run` or by ensuring PYTHONPATH is set.

  Command:
    uv run python packages/arbolab/examples/lab_open_minimal/main.py
"""
import shutil
from pathlib import Path

from arbolab.lab import Lab
from arbolab.models.core import Project
from arbolab_logger import LoggerConfig, configure_logger, get_logger

# 1. Setup Logging (Global Config for the runtime)
configure_logger(LoggerConfig(
    level="DEBUG", 
    colorize=True, 
    log_to_file=True,
    log_file_path="./example_workspace/logs/arbolab.log"
))

# User might get a logger for their own scripts
logger = get_logger("user_script") 

def main():
    # Define roots
    base_root = Path("packages/arbolab/examples/lab_open_minimal/example_workspace")
    input_root = base_root / "input"
    workspace_root = base_root / "workspace"
    results_root = base_root / "results"

    # Cleanup for clean run
    if base_root.exists():
        shutil.rmtree(base_root)
    
    input_root.mkdir(parents=True)
    
    # 2. Open Lab
    lab = Lab.open(
        workspace_root=workspace_root,
        input_root=input_root,
        results_root=results_root
    )
    
    # 3. Domain Operation (Create Project)
    # Using the Recipe-aware method instead of direct session.add()
    project = lab.define_project(name="My First Project", description="Created via minimal example")
        
    logger.info("First run complete. Testing persistence...")

    # 4. Re-open Lab (Persistence Check)
    logger.info("Re-opening Lab using ONLY workspace_root (expecting roots to be restored)...")
    lab_reopened = Lab.open(workspace_root=workspace_root)
    
    if str(lab_reopened.input_root) == str(input_root.resolve()):
        logger.info(f"Restored Input Root correctly: {lab_reopened.input_root}")
    else:
        logger.error(f"Failed to restore Input Root! Got: {lab_reopened.input_root}, Expected: {input_root.resolve()}")
        
    logger.info("Verification successful!")

if __name__ == "__main__":
    main()
