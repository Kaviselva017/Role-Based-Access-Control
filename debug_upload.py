import requests
import os

API_BASE = "https://role-based-access-control-q1et.onrender.com"
USERNAME = "admin"
PASSWORD = "admin123"

def test_upload():
    login = requests.post(f"{API_BASE}/api/auth/login", json={"username": USERNAME, "password": PASSWORD})
    token = login.json()['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test file
    test_file = r"D:\tmp\fintech-data-tmp\Finance\financial_summary.md"
    
    with open(test_file, 'rb') as f:
        resp = requests.post(
            f"{API_BASE}/api/documents/upload",
            headers=headers,
            files={'file': (os.path.basename(test_file), f)},
            data={'department': 'Finance'}
        )
    
    print(f"Status Code: {resp.status_code}")
    print(f"Headers: {resp.headers}")
    print(f"Body: {resp.text[:2000]}")

if __name__ == "__main__":
    test_upload()
