from pymongo import MongoClient

def run_check():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['company_chatbot_rbac']
        
        users = list(db['users'].find())
        print(f"Total Users Found: {len(users)}")
        
        admin_found = False
        for u in users:
            username = u.get("username")
            role = u.get("role")
            print(f" - {username} (Role: {role})")
            if username == 'admin':
                admin_found = True
        
        if admin_found:
            print("\n✅ Admin user 'admin' EXISTS.")
        else:
            print("\n❌ Admin user 'admin' NOT FOUND.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_check()
