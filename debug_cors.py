import requests

url = "https://role-based-access-control-q1et.onrender.com/api/documents/upload"
headers = {"Origin": "https://role-based-access-control-kaviselva017s-projects.vercel.app"}

# First try an OPTIONS request
try:
    print("Sending OPTIONS request...")
    resp = requests.options(url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print("Headers:")
    for k, v in resp.headers.items():
        print(f"  {k}: {v}")
except Exception as e:
    print(f"OPTIONS failed: {e}")
