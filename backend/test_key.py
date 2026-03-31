#!/usr/bin/env python3
"""Test access key verification"""

from models import access_keys_collection, users_collection
import hashlib
from datetime import datetime

print("Testing Access Key Verification")
print("=" * 60)

# Check all keys in database
print("\n1. All keys in database:")
keys = list(access_keys_collection.find({}))
print(f"   Total: {len(keys)}")

for key_doc in keys:
    print(f"\n   Key Name: {key_doc.get('name')}")
    print(f"   Hash: {key_doc['key'][:20]}...")
    print(f"   Active: {key_doc.get('is_active')}")
    print(f"   Expires: {key_doc.get('expires_at')}")
    print(f"   User ID: {key_doc.get('user_id')}")

# Test with EMP-2030
print("\n\n2. Testing EMP-2030:")
test_key = "EMP-2030"
test_hash = hashlib.sha256(test_key.encode()).hexdigest()
print(f"   Input: {test_key}")
print(f"   Hash: {test_hash}")

found = access_keys_collection.find_one({'key': test_hash})
print(f"   Found (basic query): {found is not None}")

if found:
    print(f"   Active: {found.get('is_active')}")
    print(f"   Expires: {found.get('expires_at')}")
    print(f"   Now: {datetime.utcnow()}")
    print(f"   Expires > Now: {found.get('expires_at') > datetime.utcnow()}")

# Test the full query
print("\n\n3. Testing full verify query:")
found_full = access_keys_collection.find_one({
    'key': test_hash,
    'is_active': True,
    'expires_at': {'$gt': datetime.utcnow()}
})
print(f"   Found (full query): {found_full is not None}")

if found_full:
    print(f"   ✓ Key is valid!")
else:
    print(f"   ✗ Key is invalid/expired/inactive")
    # Check individual conditions
    if not found:
        print(f"     └─ Hash doesn't match")
    elif not found.get('is_active'):
        print(f"     └─ Key is not active")
    elif not (found.get('expires_at') > datetime.utcnow()):
        print(f"     └─ Key is expired")

print("\n" + "=" * 60)
