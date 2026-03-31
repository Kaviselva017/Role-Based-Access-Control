#!/usr/bin/env python3
"""Setup demo users with access keys"""

import sys
import os

# Add backend to path for direct database access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models import User, AccessKey, users_collection, access_keys_collection
from datetime import datetime, timedelta
import hashlib
from bson import ObjectId

demo_users = [
    {
        'username': 'admin',
        'email': 'admin@test.com',
        'password': 'admin123',
        'role': 'admin',
        'department': 'Administration',
        'access_key': 'ADM-2030'
    },
    {
        'username': 'clevel_user',
        'email': 'clevel@test.com',
        'password': 'pass123',
        'role': 'c-level',
        'department': 'Executive',
        'access_key': 'CLV-2030'
    },
    {
        'username': 'finance_user',
        'email': 'finance@test.com',
        'password': 'pass123',
        'role': 'finance',
        'department': 'Finance',
        'access_key': 'FIN-2030'
    },
    {
        'username': 'hr_user',
        'email': 'hr@test.com',
        'password': 'pass123',
        'role': 'hr',
        'department': 'Human Resources',
        'access_key': 'HR-2030'
    },
    {
        'username': 'marketing_user',
        'email': 'marketing@test.com',
        'password': 'pass123',
        'role': 'marketing',
        'department': 'Marketing',
        'access_key': 'MKT-2030'
    },
    {
        'username': 'engineering_user',
        'email': 'engineering@test.com',
        'password': 'pass123',
        'role': 'engineering',
        'department': 'Engineering',
        'access_key': 'ENG-2030'
    },
    {
        'username': 'employee_user',
        'email': 'emp@test.com',
        'password': 'pass123',
        'role': 'employee',
        'department': 'General',
        'access_key': 'EMP-2030'
    },
    {
        'username': 'MARAN',
        'email': 'maran@gmail.com',
        'password': 'maran123',
        'role': 'employee',
        'department': 'General',
        'access_key': 'MAR-2030'
    }
]

def create_custom_access_key(user_id, key_str):
    """Create a custom access key (not randomly generated)"""
    key_hash = hashlib.sha256(key_str.encode()).hexdigest()
    
    # Check if key already exists
    existing = access_keys_collection.find_one({'key': key_hash})
    if existing:
        return None  # Key already exists
    
    access_key = {
        '_id': ObjectId(),
        'user_id': ObjectId(user_id),
        'key': key_hash,
        'plain_key': key_str,
        'name': key_str,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=365),
        'last_used': None,
        'is_active': True
    }
    
    result = access_keys_collection.insert_one(access_key)
    return {
        'id': str(access_key['_id']),
        'key': key_str,
        'name': access_key['name'],
        'expires_at': access_key['expires_at'].isoformat(),
        'created_at': access_key['created_at'].isoformat()
    }

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Demo User Setup with Custom Access Keys                   ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("📌 Creating demo users...")
    print("-" * 60)
    
    users_created = 0
    
    for user_data in demo_users:
        try:
            # Check if user already exists
            existing_user = User.get_user_by_username(user_data['username'])
            if existing_user:
                user_id = str(existing_user['_id'])
                print(f"⚠️  {user_data['username']:20} already exists")
            else:
                # Create user
                user = User.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    department=user_data['department']
                )
                user_id = str(user['_id'])
                print(f"✓ User: {user_data['username']:20} ({user_data['role']:12})")
                users_created += 1
            
            # Create custom access key
            key_result = create_custom_access_key(user_id, user_data['access_key'])
            if key_result:
                print(f"  └─ Key:  {user_data['access_key']:20}")
            else:
                print(f"  └─ Key:  {user_data['access_key']:20} (already exists)")
                
        except Exception as e:
            print(f"✗ Error with {user_data['username']}: {str(e)}")
    
    print("-" * 60)
    print(f"\n✓ Setup complete: {users_created} users created\n")
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔑 LOGIN CREDENTIALS FOR TESTING                          ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("📍 METHOD 1: Using Access Keys (Recommended)")
    print("-" * 60)
    for user in demo_users:
        print(f"  {user['role']:12} | Key: {user['access_key']}")
    
    print("\n📍 METHOD 2: Using Username & Password")
    print("-" * 60)
    for user in demo_users:
        print(f"  {user['role']:12} | {user['username']:20} / {user['password']}")
    
    print("\n" + "=" * 60)
    print("✓ Ready to test!")
    print("  URL: http://localhost:3000")
    print("  • Use Access Key (e.g., ADM-2030)")
    print("  • OR use Username/Password")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("  Make sure MongoDB is running at localhost:27017")
        sys.exit(1)

