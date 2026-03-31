#!/usr/bin/env python3
"""Debug authentication issue"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models import User, AccessKey, access_keys_collection, users_collection
import hashlib

print("=" * 60)
print("Checking Demo Users and Access Keys")
print("=" * 60)

# Check users
print("\n📌 Users in database:")
print("-" * 60)
users = list(users_collection.find({}))
print(f"Total users: {len(users)}")
for user in users:
    print(f"  • {user['username']:20} ({user['role']:12}) - Active: {user.get('is_active', 'N/A')}")

# Check access keys
print("\n📌 Access Keys in database:")
print("-" * 60)
keys = list(access_keys_collection.find({}))
print(f"Total keys: {len(keys)}")
for key in keys:
    print(f"  • {key.get('name', 'N/A'):20} - Hash: {key['key'][:10]}... - Active: {key.get('is_active', 'N/A')}")

# Test verification with EMP-2030
print("\n📌 Testing Verification:")
print("-" * 60)
test_key = "EMP-2030"
print(f"Testing key: {test_key}")

# Hash it the same way as the backend
key_hash = hashlib.sha256(test_key.encode()).hexdigest()
print(f"Hash: {key_hash}")

# Check if this hash exists
found_key = access_keys_collection.find_one({'key': key_hash})
if found_key:
    print(f"✓ Key found in database!")
    print(f"  User ID: {found_key.get('user_id')}")
    print(f"  Active: {found_key.get('is_active')}")
    print(f"  Expires: {found_key.get('expires_at')}")
else:
    print(f"✗ Key NOT found in database")
    print("\nAll key hashes in database:")
    for key in keys:
        print(f"  • {key['key']}")

print("\n" + "=" * 60)
