import requests
import sys

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Check Login Redirect
print("1. Checking Login Redirect...")
try:
    r = requests.get(BASE_URL, allow_redirects=False)
    if r.status_code == 307 and r.headers["location"] == "/auth/login":
        print("PASS: Redirects to /auth/login")
    else:
        print(f"FAIL: Status {r.status_code}, Location: {r.headers.get('location')}")
except Exception as e:
    print(f"FAIL: Connection error {e}")

# 2. Check /workspaces/new endpoint existence
print("\n2. Checking /workspaces/new existence...")
# Note: This requires auth usually, so we expect a redirect to login if we hit it without cookies
# OR if we just check if it doesn't 404
try:
    r = requests.get(f"{BASE_URL}/workspaces/new", allow_redirects=False)
    if r.status_code == 307 and r.headers["location"] == "/auth/login":
         print("PASS: /workspaces/new attempts auth (redirects to login)")
    elif r.status_code == 200:
         print("PASS: /workspaces/new accessible")
    else:
         print(f"FAIL: Unexpected status {r.status_code}")
except Exception as e:
    print(f"FAIL: Connection error {e}")
