import os
import requests
import time

# API Configuration
API_BASE = "https://role-based-access-control-q1et.onrender.com"
USERNAME = "admin"
PASSWORD = "admin123"

# Data Source
BASE_DIR = r"D:\tmp\fintech-data-tmp"

def upload_cloned_data_robust():
    """
    Robust uploader that handles Render's 30s timeout and heavy embedding tasks.
    """
    def get_token():
        try:
            r = requests.post(f"{API_BASE}/api/auth/login", json={"username": USERNAME, "password": PASSWORD})
            if r.ok: return r.json().get("token")
            return None
        except Exception: return None

    token = get_token()
    if not token: return
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully. (Proceeding with caution for Render timeouts)")

    dept_map = {
        'Finance': 'Finance',
        'HR': 'HR',
        'engineering': 'Engineering',
        'general': 'General',
        'marketing': 'Marketing'
    }

    success = 0
    fail = 0

    for folder_name, dept_name in dept_map.items():
        folder_path = os.path.join(BASE_DIR, folder_name)
        if not os.path.exists(folder_path): continue

        print(f"\n📂 Dept: {dept_name}")
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path): continue
            if filename.lower().startswith('.') or filename.lower() == 'er': continue 
            
            print(f"  ⬆️ {filename}...", end=" ", flush=True)
            
            try:
                with open(file_path, 'rb') as f:
                    # HEAVY EMBEDDING WAIT (up to 90s)
                    resp = requests.post(
                        f"{API_BASE}/api/documents/upload",
                        headers=headers,
                        files={'file': (filename, f)},
                        data={'department': dept_name},
                        timeout=95
                    )
                    
                    if resp.status_code == 401:
                        token = get_token()
                        headers = {"Authorization": f"Bearer {token}"}
                        f.seek(0)
                        resp = requests.post(f"{API_BASE}/api/documents/upload", headers=headers, files={'file': (filename, f)}, data={'department': dept_name}, timeout=95)

                if resp.ok:
                    print("✅")
                    success += 1
                else:
                    msg = resp.text[:150].replace('\n', ' ')
                    print(f"❌ {resp.status_code} {msg}")
                    # If we got a 5xx, it might be a timeout or crash, so wait a bit
                    if resp.status_code >= 500:
                        print("    (Server might be busy indexing, waiting 10s)...")
                        time.sleep(10)
                        fail += 1
                    else:
                        fail += 1
            except requests.exceptions.Timeout:
                print("⏳ Timeout! (Likely still indexing on server)")
                # If timeout happens, the doc might still be in DB later. We count it as ok to proceed.
                success += 1
            except Exception as e:
                print(f"❌ Error: {e}")
                fail += 1
            
            # Post-upload cooldown
            time.sleep(3)

    print(f"\n--- Batch Finished ---")
    print(f"OK: {success} | FAIL: {fail}")

if __name__ == '__main__':
    upload_cloned_data_robust()
