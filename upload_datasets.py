"""
Auto-upload all downloaded datasets to the live Dragon Intel API.
Maps each file to its correct department for RBAC filtering.
"""
import requests
import os
import time

API_BASE = "https://dragon-intel-chatbot-api.onrender.com"
USERNAME = "admin"
PASSWORD = "admin123"

# Map: (local file path, department for RBAC)
DATASETS = [
    ("datasets/finance/financial_summary.md", "Finance"),
    ("datasets/finance/quarterly_financial_report.md", "Finance"),
    ("datasets/hr/hr_data.csv", "HR"),
    ("datasets/engineering/engineering_master_doc.md", "Engineering"),
    ("datasets/marketing/marketing_report_2024.md", "Marketing"),
    ("datasets/marketing/marketing_report_q1_2024.md", "Marketing"),
    ("datasets/marketing/marketing_report_q2_2024.md", "Marketing"),
    ("datasets/marketing/marketing_report_q3_2024.md", "Marketing"),
    ("datasets/marketing/market_report_q4_2024.md", "Marketing"),
    ("datasets/general/employee_handbook.md", "General"),
]

def upload_all():
    print(f"Logging into {API_BASE}...")
    login = requests.post(f"{API_BASE}/api/auth/login", json={
        "username": USERNAME, "password": PASSWORD
    })
    
    if not login.ok:
        print(f"Login failed: {login.text}")
        return
    
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful!\n")
    
    success = 0
    failed = 0
    
    for filepath, department in DATASETS:
        filename = os.path.basename(filepath)
        
        if not os.path.exists(filepath):
            print(f"  SKIP {filename} — file not found at {filepath}")
            failed += 1
            continue
        
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  Uploading {filename} ({size_kb:.1f} KB) → {department}...", end=" ")
        
        with open(filepath, "rb") as f:
            resp = requests.post(
                f"{API_BASE}/api/documents/upload",
                headers=headers,
                files={"file": (filename, f)},
                data={"department": department}
            )
        
        if resp.ok:
            print("✅")
            success += 1
        else:
            print(f"❌ {resp.text[:100]}")
            failed += 1
        
        time.sleep(1)  # Give the server time to process embeddings
    
    print(f"\n{'='*50}")
    print(f"Upload complete: {success} succeeded, {failed} failed")
    print(f"{'='*50}")

if __name__ == "__main__":
    upload_all()
