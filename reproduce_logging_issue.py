
from arbolab.lab import Lab
import logging
import shutil
from pathlib import Path

def setup():
    # Clean previous run
    if Path("test_lab_lifecycle").exists():
        shutil.rmtree("test_lab_lifecycle")

def run_lifecycle(run_id):
    with open("handler_counts.txt", "a") as f:
        f.write(f"Run {run_id}: Handlers before: {len(logging.getLogger('arbolab').handlers)}\n")
    
    # Open Lab (creates logs)
    lab = Lab.open("test_lab_lifecycle")
    
    with open("handler_counts.txt", "a") as f:
        f.write(f"Run {run_id}: Handlers during: {len(logging.getLogger('arbolab').handlers)}\n")
    
    # Proper close
    lab.close()
    
    with open("handler_counts.txt", "a") as f:
        f.write(f"Run {run_id}: Handlers after: {len(logging.getLogger('arbolab').handlers)}\n")

if Path("handler_counts.txt").exists():
    Path("handler_counts.txt").unlink()

setup()
run_lifecycle(1)
run_lifecycle(2)
run_lifecycle(3)
