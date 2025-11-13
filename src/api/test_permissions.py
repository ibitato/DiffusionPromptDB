"""Test permissions system"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 70)
print("Testing Permissions System")
print("=" * 70)

# 1. Login as test user
print("\n1. Login as test user...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "test", "password": "test"}
)
if response.status_code == 200:
    test_token = response.json()["access_token"]
    test_user = response.json()["user"]
    print(f"✅ Logged in as: {test_user['username']} (role: {test_user['role']})")
else:
    print(f"❌ Login failed: {response.text}")
    exit(1)

# 2. Try to delete a preloaded prompt (should fail)
print("\n2. Try to delete preloaded prompt #3 (should fail)...")
response = requests.delete(
    f"{BASE_URL}/prompts/3",
    headers={"Authorization": f"Bearer {test_token}"}
)
if response.status_code == 403:
    print(f"✅ Correctly blocked: {response.json()['detail']}")
elif response.status_code == 204:
    print("❌ SECURITY ISSUE: User was able to delete preloaded prompt!")
else:
    print(f"⚠️  Unexpected response: {response.status_code} - {response.text}")

# 3. Try to create a prompt (should SUCCEED)
print("\n3. Try to create a prompt as regular user (should succeed)...")
response = requests.post(
    f"{BASE_URL}/prompts/",
    headers={"Authorization": f"Bearer {test_token}"},
    json={"text": "Test prompt by regular user"}
)
if response.status_code == 201:
    created_prompt = response.json()
    print(f"✅ User can create their own prompts (ID: {created_prompt['id']})")
    user_prompt_id = created_prompt['id']
else:
    print(f"❌ User blocked from creating: {response.status_code} - {response.text}")
    user_prompt_id = None

# 3b. Try to edit own prompt (should succeed)
if user_prompt_id:
    print(f"\n3b. Try to edit own prompt #{user_prompt_id} (should succeed)...")
    response = requests.put(
        f"{BASE_URL}/prompts/{user_prompt_id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"text": "Updated by owner"}
    )
    if response.status_code == 200:
        print("✅ User can edit their own prompts")
    else:
        print(f"❌ User blocked from editing own prompt: {response.status_code}")

# 3c. Try to delete own prompt (should succeed)
if user_prompt_id:
    print(f"\n3c. Try to delete own prompt #{user_prompt_id} (should succeed)...")
    response = requests.delete(
        f"{BASE_URL}/prompts/{user_prompt_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    if response.status_code == 204:
        print("✅ User can delete their own prompts")
    else:
        print(f"❌ User blocked from deleting own prompt: {response.status_code}")

# 4. Login as admin
print("\n4. Login as admin user...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "admin"}
)
if response.status_code == 200:
    admin_token = response.json()["access_token"]
    admin_user = response.json()["user"]
    print(f"✅ Logged in as: {admin_user['username']} (role: {admin_user['role']})")
else:
    print(f"❌ Login failed: {response.text}")
    exit(1)

# 5. Try to delete preloaded prompt as admin (should succeed)
print("\n5. Try to update preloaded prompt #2 as admin (should succeed)...")
response = requests.put(
    f"{BASE_URL}/prompts/2",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={"text": "Updated by admin"}
)
if response.status_code == 200:
    print("✅ Admin can modify preloaded prompts")
elif response.status_code == 403:
    print("❌ SECURITY ISSUE: Admin blocked from modifying!")
else:
    print(f"⚠️  Unexpected response: {response.status_code} - {response.text}")

print("\n" + "=" * 70)
print("Test Complete")
print("=" * 70)
