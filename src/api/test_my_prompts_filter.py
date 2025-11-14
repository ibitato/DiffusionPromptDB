#!/usr/bin/env python3
"""
Debug script for my_prompts filter
"""

import requests

BASE_URL = "http://localhost:8000"
API_KEY = "test_key_12345"

# Test user credentials
TEST_USER = {
    "username": "test",
    "password": "test123"
}

print("="*60)
print("  Testing my_prompts Filter Debug")
print("="*60)

# Login
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json=TEST_USER,
    headers={"X-API-Key": API_KEY}
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    exit(1)

token = response.json().get("access_token")
print(f"✅ Logged in as: {TEST_USER['username']}")
print(f"   Token: {token[:30]}...")

# Test 1: Search without my_prompts filter
print("\n" + "-"*60)
print("Test 1: Search WITHOUT my_prompts filter")
print("-"*60)
response = requests.get(
    f"{BASE_URL}/api/v1/search/complex",
    params={"limit": 5},
    headers={
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}"
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Total results: {data['total']}")
    print(f"   Returned: {len(data['results'])} prompts")
    
    for i, result in enumerate(data['results'][:3], 1):
        created_by = result.get('created_by')
        print(f"\n   Result {i}:")
        print(f"   - ID: {result['id']}")
        print(f"   - Created by: {created_by}")
        print(f"   - Text: {result['original_prompt'][:50]}...")
else:
    print(f"❌ Search failed: {response.status_code}")
    print(f"   Response: {response.text}")

# Test 2: Search WITH my_prompts filter
print("\n" + "-"*60)
print("Test 2: Search WITH my_prompts=true filter")
print("-"*60)
response = requests.get(
    f"{BASE_URL}/api/v1/search/complex",
    params={"my_prompts": True, "limit": 5},
    headers={
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}"
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Total results with my_prompts: {data['total']}")
    print(f"   Returned: {len(data['results'])} prompts")
    
    if len(data['results']) == 0:
        print("\n   ⚠️  No prompts found for this user!")
        print("   This could mean:")
        print("   - User has not created any prompts yet")
        print("   - Filter is working correctly")
    else:
        for i, result in enumerate(data['results'][:3], 1):
            created_by = result.get('created_by')
            print(f"\n   Result {i}:")
            print(f"   - ID: {result['id']}")
            print(f"   - Created by: {created_by}")
            print(f"   - Text: {result['original_prompt'][:50]}...")
else:
    print(f"❌ Search failed: {response.status_code}")
    print(f"   Response: {response.text}")

# Test 3: Create a test prompt to verify user_id
print("\n" + "-"*60)
print("Test 3: Create a test prompt")
print("-"*60)

prompt_data = {
    "text": "Test prompt for my_prompts filter verification",
    "tags": "test-filter",
    "rating": 5
}

response = requests.post(
    f"{BASE_URL}/api/v1/prompts/",
    json=prompt_data,
    headers={
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}"
    }
)

if response.status_code == 201:
    data = response.json()
    prompt_id = data['id']
    created_by = data.get('created_by')
    print(f"✅ Prompt created!")
    print(f"   ID: {prompt_id}")
    print(f"   Created by: {created_by}")
    
    # Test 4: Search again with my_prompts filter
    print("\n" + "-"*60)
    print("Test 4: Search WITH my_prompts after creating")
    print("-"*60)
    response = requests.get(
        f"{BASE_URL}/api/v1/search/complex",
        params={"my_prompts": True, "limit": 5},
        headers={
            "X-API-Key": API_KEY,
            "Authorization": f"Bearer {token}"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total results: {data['total']}")
        
        found_test_prompt = False
        for result in data['results']:
            if result['id'] == prompt_id:
                found_test_prompt = True
                print(f"\n   ✅ Found our test prompt (ID: {prompt_id})")
                print(f"      Created by: {result.get('created_by')}")
                break
        
        if not found_test_prompt and data['total'] > 0:
            print(f"\n   ⚠️  Test prompt not in first {len(data['results'])} results")
    
    # Cleanup
    print("\n" + "-"*60)
    print("Cleanup: Deleting test prompt")
    print("-"*60)
    response = requests.delete(
        f"{BASE_URL}/api/v1/prompts/{prompt_id}",
        headers={
            "X-API-Key": API_KEY,
            "Authorization": f"Bearer {token}"
        }
    )
    print(f"✅ Test prompt deleted" if response.status_code == 204 else f"⚠️  Delete status: {response.status_code}")

print("\n" + "="*60)
print("  Debug Complete!")
print("="*60)
