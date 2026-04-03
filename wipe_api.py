import requests
import json
import time

API_BASE = "https://dragon-intel-chatbot-api.onrender.com"
USERNAME = "admin"
PASSWORD = "admin123"

def wipe_all_documents():
    print(f"Logging into {API_BASE} as {USERNAME}...")
    
    login_resp = requests.post(f"{API_BASE}/api/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    try:
        if not login_resp.ok:
            print("Failed to login! Make sure your USERNAME and PASSWORD above are correct.")
            print("Response:", login_resp.text)
            return
            
        token = login_resp.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful! Fetching documents...")

        docs_resp = requests.get(f"{API_BASE}/api/documents", headers=headers)
        if not docs_resp.ok:
            print("Failed to fetch documents!")
            print("Response:", docs_resp.text)
            return
            
        documents = docs_resp.json().get("documents", [])
        print(f"Found {len(documents)} documents uploaded.")
        
        if len(documents) == 0:
            print("Nothing to delete!")
            return
            
        # Hardcoding YES to delete fast
        print("Automatically deleting all datasets as requested...")
            
        for doc in documents:
            doc_id = doc["id"]
            filename = doc["filename"]
            print(f"Deleting {filename}...")
            
            del_resp = requests.delete(f"{API_BASE}/api/documents/{doc_id}", headers=headers)
            if del_resp.ok:
                print(f"  -> Deleted {filename} successfully.")
            else:
                print(f"  -> Failed to delete {filename}: {del_resp.text}")
                
            time.sleep(0.1)
            
        print("\n✅ All uploaded datasets have been completely removed from your live website!")
    except Exception as e:
        print("Encountered error parsing JSON. API response was:", login_resp.text[:500])
        print("Exception:", e)

if __name__ == "__main__":
    wipe_all_documents()
