from fastapi.testclient import TestClient
from apps.web.main import app
import sys

client = TestClient(app)

def test_status():
    print("Testing /api/system/status...")
    response = client.get("/api/system/status")
    
    if response.status_code != 200:
        print(f"FAILED: Status code {response.status_code}")
        print(response.text)
        sys.exit(1)
        
    data = response.json()
    print("Response JSON:", data)
    
    required_keys = ["versions", "postgres", "lab", "role"]
    for key in required_keys:
        if key not in data:
            print(f"FAILED: Missing key '{key}'")
            sys.exit(1)
            
    if "web" not in data["versions"] or "core" not in data["versions"]:
        print("FAILED: Missing version info")
        sys.exit(1)
        
    print("SUCCESS: Endpoint returned valid structure.")

if __name__ == "__main__":
    try:
        test_status()
    except Exception as e:
        print(f"FAILED with exception: {e}")
        sys.exit(1)
