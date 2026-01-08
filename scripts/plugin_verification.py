
import importlib.metadata
import sys
from pathlib import Path

# Add core package to path if not installed
sys.path.append(str(Path(__file__).parent.parent / "packages/core/src"))

from arbolab.plugins import PluginRegistry

def verify_plugins():
    print("Verifying plugins...")
    
    # 1. Check entry points directly
    # Note: this relies on installed metadata, which might be stale if not synced
    eps = importlib.metadata.entry_points(group="arbolab.plugins")
    found = {ep.name: ep for ep in eps}
    
    print(f"Found entry points: {list(found.keys())}")
    
    # 2. Check PluginRegistry with manual path injection ensures modules are loadable
    # but discover() relies on entry_points().
    
    first_check = list(set(["ls3", "ptq", "treeqinetic"]) & set(found.keys()))
    print(f"Checking for known plugins: {first_check}")

    registry = PluginRegistry()
    registry.discover(["ls3", "treeqinetic"])
    
    ls3 = registry.get_plugin("ls3")
    ptq = registry.get_plugin("treeqinetic")
    
    if ls3:
        print(f"PASS: ls3 loaded: {ls3}")
        if hasattr(ls3, 'register'):
             print("PASS: ls3 has register()")
        else:
             print("FAIL: ls3 missing register()")
    else:
        print("WARN: ls3 not loaded by registry (might need uv sync)")

    if ptq:
        print(f"PASS: treeqinetic loaded: {ptq}")
        if hasattr(ptq, 'register'):
             print("PASS: treeqinetic has register()")
        else:
             print("FAIL: treeqinetic missing register()")
    else:
        print("WARN: treeqinetic not loaded by registry (might need uv sync)")

if __name__ == "__main__":
    verify_plugins()
