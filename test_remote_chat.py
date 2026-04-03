import requests
import sys

API_URL = "https://role-based-access-control-q1et.onrender.com"

print("1. Logging in...")
login_res = requests.post(f"{API_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})

if not login_res.ok:
    print(f"Login failed: {login_res.status_code}")
    print(login_res.text)
    sys.exit(1)

token = login_res.json().get("token")
print(f"Token obtained.")

print("2. Testing chat with 'Need better ways to work'...")
chat_res = requests.post(f"{API_URL}/api/chat", json={
    "query": "Need better ways to work"
}, headers={
    "Authorization": f"Bearer {token}"
})

print(f"Status: {chat_res.status_code}")
print("Response JSON:")
print(chat_res.text)
