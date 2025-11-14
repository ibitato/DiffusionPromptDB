#!/usr/bin/env python3
"""
Simple API test - Direct endpoint testing
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "REDACTED_TEST_KEY"

print("=" * 70)
print("  SIMPLE API TEST - Direct Endpoint Testing")
print("=" * 70)

# Step 1: Login
print("\n1. Login as 'test' user")
print("-" * 70)
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "test", "password": "test123"},
    headers={"X-API-Key": API_KEY},
)
print(f"Status: {response.status_code}")

if response.status_code != 200:
    print(f"❌ Cannot continue: {response.text}")
    exit(1)

token = response.json()["access_token"]
user_id = (
    requests.get(
        f"{BASE_URL}/auth/me",
        headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
    )
    .json()
    .get("id", "unknown")
)

print(f"✅ Logged in")
print(f"   User ID: {user_id}")

# Step 2: Search ALL prompts (no filters)
print("\n2. Search ALL prompts (no my_prompts filter)")
print("-" * 70)
response = requests.get(
    f"{BASE_URL}/search/complex",
    params={"limit": 20},
    headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    total = data["total"]
    results = data["results"]
    print(f"✅ Total prompts in DB: {total}")
    print(f"   Returned: {len(results)}")

    # Show created_by of first 3
    print("\n   First 3 prompts:")
    for i, r in enumerate(results[:3], 1):
        print(f"   {i}. ID={r['id']}, created_by={r.get('created_by')}")
else:
    print(f"❌ Failed: {response.text}")

# Step 3: Search with my_prompts=true
print("\n3. Search with my_prompts=true")
print("-" * 70)
response = requests.get(
    f"{BASE_URL}/search/complex",
    params={"my_prompts": "true", "limit": 20},
    headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    total = data["total"]
    results = data["results"]
    print(f"✅ My prompts only: {total}")
    print(f"   Returned: {len(results)}")

    if results:
        print("\n   My prompts:")
        for i, r in enumerate(results[:5], 1):
            print(f"   {i}. ID={r['id']}, created_by={r.get('created_by')}")
    else:
        print("\n   ℹ️  No prompts created by this user yet")
else:
    print(f"❌ Failed: {response.text}")

# Step 4: Test my_prompts with art_style filter
print("\n4. Test my_prompts with art_style filter")
print("-" * 70)
response = requests.get(
    f"{BASE_URL}/search/complex",
    params={"my_prompts": "true", "art_style": "realistic", "limit": 20},
    headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ My realistic prompts: {data['total']}")
else:
    print(f"❌ Failed: {response.text}")

print("\n" + "=" * 70)
print("  Test Complete - Check console output from backend")
print("=" * 70)
print("\nℹ️  If 'DEBUG: Filtering by user_id=X' appears in backend logs,")
print("   the filter is being applied correctly.")
