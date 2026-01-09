from arbolab.config import LabConfig
try:
    config = LabConfig()
    config.data_root = "new_path"
    print("FAILED: LabConfig is not frozen!")
except Exception as e:
    print(f"SUCCESS: LabConfig is frozen. Error: {e}")
