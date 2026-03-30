#!/usr/bin/env python3
"""Setup demo users via HTTP API"""

import requests
import json
import time
import sys

# Flask backend URL
BASE_URL = 'http://localhost:5000'

demo_users = [
    {
        'username': 'admin',
        'email': 'admin@test.com',
        'password': 'admin123',
        'role': 'admin',
        'department': 'Administration'
    },
    {
        'username': 'clevel_user',
        'email': 'clevel@test.com',
        'password': 'pass123',
        'role': 'c-level',
        'department': 'Executive'
    },
    {
        'username': 'finance_user',
        'email': 'finance@test.com',
        'password': 'pass123',
        'role': 'finance',
        'department': 'Finance'
    },
    {
        'username': 'hr_user',
        'email': 'hr@test.com',
        'password': 'pass123',
        'role': 'hr',
        'department': 'Human Resources'
    },
    {
        'username': 'employee_user',
        'email': 'emp@test.com',
        'password': 'pass123',
        'role': 'employee',
        'department': 'General'
    }
]

def register_user(user_data):
    """Register a user via the API"""
    try:
        response = requests.post(
            f'{BASE_URL}/api/auth/register',
            json=user_data,
            timeout=5
        )
        return response.status_code, response.json()
    except requests.ConnectionError:
        return None, 'Connection failed'
    except Exception as e:
        return None, str(e)

def main():
    print("Demo User Setup via API")
    print("=" * 60)
    print(f"Backend URL: {BASE_URL}")
    print()
    
    # Check if backend is running
    print("Checking if backend is running...")
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=2)
        print("✓ Backend is running!")
    except:
        print("✗ Backend is not running at", BASE_URL)
        print("  Please start the Flask backend first:")
        print("  cd backend && python app.py")
        sys.exit(1)
    
    print()
    print("Creating demo users...")
    print("-" * 60)
    
    created = 0
    failed = 0
    
    for user in demo_users:
        status, response = register_user(user)
        
        if status == 201:
            print(f"✓ Created {user['username']} ({user['role']})")
            created += 1
        elif status == 400:
            # User might already exist
            if 'already' in str(response).lower() or 'exists' in str(response).lower():
                print(f"⚠️  {user['username']} already exists")
            else:
                print(f"✗ Failed to create {user['username']}: {response.get('message', response)}")
                failed += 1
        else:
            print(f"✗ Failed to create {user['username']}: {response}")
            failed += 1
        
        time.sleep(0.5)  # Small delay between requests
    
    print("-" * 60)
    print(f"\nDemo Setup Complete!")
    print(f"✓ Created: {created}")
    if failed > 0:
        print(f"✗ Failed: {failed}")
    print()
    print("You can now login with:")
    for user in demo_users:
        print(f"  {user['username']} / {user['password']} (Role: {user['role']})")

if __name__ == '__main__':
    main()
