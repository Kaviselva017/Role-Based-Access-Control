"""
Upload remaining datasets one at a time with longer delay to let the server process embeddings.
"""
import requests
import os
import time

API_BASE = "https://dragon-intel-api.onrender.com"
USERNAME = "admin"
PASSWORD = "admin123"

# Only the files that failed (skip the 2 finance files already uploaded)
REMAINING = [
    ("datasets/hr/hr_data.csv", "HR"),
    ("datasets/engineering/engineering_master_doc.md", "Engineering"),
    ("datasets/marketing/marketing_report_2024.md", "Marketing"),
    ("datasets/marketing/marketing_report_q1_2024.md", "Marketing"),
    ("datasets/marketing/marketing_report_q2_2024.md", "Marketing"),
    ("datasets/marketing/marketing_report_q3_2024.md", "Marketing"),
    ("datasets/marketing/market_report_q4_2024.md", "Marketing"),
    ("datasets/general/employee_handbook.md", "General"),
]

def upload_remaining():
    print(f"Logging into {API_BASE}...")
    login = requests.post(f"{API_BASE}/api/auth/login", json={
        "username": USERNAME, "password": PASSWORD
    }, timeout=30)
    
    if not login.ok:
        print(f"Login failed: {login.text}")
        return
    
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful!\n")
    
    for filepath, department in REMAINING:
        filename = os.path.basename(filepath)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"Uploading {filename} ({size_kb:.1f} KB) -> {department}...", end=" ", flush=True)
        
        try:
            with open(filepath, "rb") as f:
                resp = requests.post(
                    f"{API_BASE}/api/documents/upload",
                    headers=headers,
                    files={"file": (filename, f)},
                    data={"department": department},
                    timeout=120  # 2 min timeout for embedding processing
                )
            
            if resp.ok:
                print("✅")
            else:
                print(f"❌ {resp.text[:150]}")
        except Exception as e:
            print(f"❌ {e}")
        
        # Give the server 5 seconds to recover before next upload
        print("  Waiting 5s for server to process...", flush=True)
        time.sleep(5)
    
    print("\nDone! Run check_docs.py to verify.")

if __name__ == "__main__":
    upload_remaining()
