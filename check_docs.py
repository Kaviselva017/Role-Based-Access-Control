import requests

r = requests.post('https://dragon-intel-api.onrender.com/api/auth/login', json={'username':'admin','password':'admin123'})
token = r.json()['token']
docs = requests.get('https://dragon-intel-api.onrender.com/api/documents', headers={'Authorization': f'Bearer {token}'})
data = docs.json()
print(f"Total documents: {len(data.get('documents',[]))}")
for d in data.get('documents', []):
    print(f"  - {d['filename']} | Dept: {d['department']} | Indexed: {d.get('indexed', False)}")
