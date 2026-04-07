
import requests
import os
import time

API_BASE = "https://dragon-intel-chatbot-api.onrender.com"
USERNAME = "admin"
PASSWORD = "admin123"

# Mapping from local path to RBAC department
NEW_DATASETS = [
    ("datasets/general/employees.md", "General"),
    ("datasets/finance/finance.md", "Finance"),
    ("datasets/hr/hr.md", "HR"),
    ("datasets/marketing/marketing.md", "Marketing"),
    ("datasets/engineering/engineering.md", "Engineering"),
]


def upload_new_files():
    global API_BASE
    print(f"Connecting to Dragon Intel API at {API_BASE}...")
    try:
        login = requests.post(f"{API_BASE}/api/auth/login", json={
            "username": USERNAME, "password": PASSWORD
        }, timeout=10)
    except Exception as e:
        # Try local fallback if production is down or unreachable
        print(f"Production login failed ({e}), trying local...")
        API_BASE_LOCAL = "http://localhost:5000"
        try:
            login = requests.post(f"{API_BASE_LOCAL}/api/auth/login", json={
                "username": USERNAME, "password": PASSWORD
            }, timeout=5)
            if login.ok:
                API_BASE = API_BASE_LOCAL
        except:
            print("Both production and local APIs are unreachable.")
            return

    if not login.ok:
        print(f"Login failed: {login.text}")
        return
    
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Login successful to {API_BASE}!\n")
    
    for filepath, department in NEW_DATASETS:
        filename = os.path.basename(filepath)
        if not os.path.exists(filepath):
            print(f"  [Error] Skipping {filename}: File not found.")
            continue
            
        print(f"  Uploading {filename} to {department} department...", end=" ", flush=True)
        with open(filepath, "rb") as f:
            resp = requests.post(
                f"{API_BASE}/api/documents/upload",
                headers=headers,
                files={"file": (filename, f)},
                data={"department": department}
            )
        
        if resp.ok:
            print("✅ Success")
        else:
            print(f"❌ Failed ({resp.status_code})")
            print(f"    Detail: {resp.text[:100]}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    # Fix the typo in my variable name USERNAMe -> USERNAME
    USERNAMe = USERNAME 
    upload_new_files()
