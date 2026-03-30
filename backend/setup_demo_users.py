#!/usr/bin/env python3
"""Setup demo users for testing"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import User, users_collection

def setup_demo_users():
    """Create demo users for testing all 5 roles"""
    
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
    
    print("Setting up demo users...")
    print("-" * 50)
    
    for user_data in demo_users:
        try:
            # Check if user already exists
            existing_user = User.get_user_by_username(user_data['username'])
            if existing_user:
                print(f"⚠️  User '{user_data['username']}' already exists. Skipping...")
                continue
            
            # Create new user
            user = User.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                role=user_data['role'],
                department=user_data['department']
            )
            
            print(f"✓ Created user: {user_data['username']} ({user_data['role']})")
            print(f"  Email: {user_data['email']}")
            print(f"  Password: {user_data['password']}")
            print(f"  Department: {user_data['department']}")
            print()
            
        except Exception as e:
            print(f"✗ Failed to create user '{user_data['username']}': {str(e)}")
            print()
    
    print("-" * 50)
    print("Demo user setup complete!")
    print("\nYou can now login with any of the demo credentials on the login page.")

if __name__ == '__main__':
    setup_demo_users()
