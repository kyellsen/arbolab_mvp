import requests
import time

BASE_URL = "http://localhost:8000"

def test_crud_cascade():
    print("--- Starting CRUD & Cascade Verification ---", flush=True)
    
    # 1. Create a Project
    project_data = {"name": "Test Project", "description": "Cascade test"}
    resp = requests.post(f"{BASE_URL}/api/entities/project", json=project_data)
    if resp.status_code != 200:
        print(f"FAILED: Could not create project. {resp.text}")
        return
    project = resp.json()
    project_id = project['id']
    print(f"CREATED Project: ID={project_id}", flush=True)

    # 2. Create an Experiment linked to the Project
    experiment_data = {"project_id": project_id, "name": "Test Experiment"}
    resp = requests.post(f"{BASE_URL}/api/entities/experiment", json=experiment_data)
    if resp.status_code != 200:
        print(f"FAILED: Could not create experiment. {resp.text}")
        return
    experiment = resp.json()
    experiment_id = experiment['id']
    print(f"CREATED Experiment: ID={experiment_id} (linked to Project {project_id})", flush=True)

    # 3. List Experiments and verify it's there
    resp = requests.get(f"{BASE_URL}/api/entities/experiment")
    experiments = resp.json()
    if not any(e['id'] == experiment_id for e in experiments):
        print("FAILED: Experiment not found in list.")
        return
    print("VERIFIED: Experiment exists in list.", flush=True)

    # 4. Delete the Project
    print(f"DELETING Project {project_id}...", flush=True)
    resp = requests.delete(f"{BASE_URL}/api/entities/project/{project_id}")
    if resp.status_code != 200:
        print(f"FAILED: Could not delete project. {resp.text}")
        return
    print("DELETED Project successfully.", flush=True)

    # 5. Verify the Experiment is also deleted (Cascade check)
    resp = requests.get(f"{BASE_URL}/api/entities/experiment")
    experiments = resp.json()
    if any(e['id'] == experiment_id for e in experiments):
        print("ALERT: Experiment still exists! Cascade DELETE failed.")
    else:
        print("SUCCESS: Experiment was automatically deleted via cascade.", flush=True)

    print("--- Verification Finished ---", flush=True)

if __name__ == "__main__":
    import sys
    try:
        test_crud_cascade()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}", flush=True)
        sys.exit(1)
