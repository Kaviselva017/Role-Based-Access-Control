from pymongo import MongoClient
import json

try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['company_chatbot_rbac']
    
    output = []
    output.append("--- Database: company_chatbot_rbac ---")
    
    users = list(db['users'].find())
    output.append(f"Total Users: {len(users)}")
    for u in users:
        output.append(f"ID: {u.get('_id')}, Username: {u.get('username')}, Role: {u.get('role')}, Dept: {u.get('department')}")
        
    keys = list(db['access_keys'].find())
    output.append(f"\nTotal Access Keys: {len(keys)}")
    for k in keys:
        output.append(f"User ID: {k.get('user_id')}, Key Name: {k.get('name')}, Key Value: {k.get('key')}, Active: {k.get('is_active')}")
    
    with open('db_check_result.txt', 'w') as f:
        f.write('\n'.join(output))
        
    print("Results saved to db_check_result.txt")
        
except Exception as e:
    print(f"Error: {e}")
