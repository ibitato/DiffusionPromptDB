#!/usr/bin/env python3
"""
Test script for new prompt fields and my_prompts filter.

Tests:
1. Create prompt with all new fields
2. Read prompt and verify fields
3. Update prompt with new fields
4. Search with my_prompts filter
5. Delete prompt
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"
API_KEY = "test_key_12345"  # From .env.example

# Test user credentials
TEST_USER = {"username": "test", "password": "test123"}


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_auth():
    """Test authentication and get token"""
    print_section("1. Testing Authentication")

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", json=TEST_USER, headers={"X-API-Key": API_KEY}
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful!")
        print(f"   Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")

        # Try to register if login failed
        print("\n   Trying to register new user...")
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={**TEST_USER, "email": "test@example.com"},
            headers={"X-API-Key": API_KEY},
        )

        if response.status_code == 201:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Registration successful!")
            print(f"   Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None


def test_create_prompt(token):
    """Test creating a prompt with all new fields"""
    print_section("2. Testing CREATE with New Fields")

    prompt_data = {
        "text": "Test prompt with all fields",
        "negative_prompt": "test negative prompt",
        "model": "test-model",
        "category": "Test Category",
        "art_style": "realistic",
        "tags": "test, api, new-fields",
        "rating": 4,
        "notes": "Test notes for new fields",
        "parameters": '{"steps": 50, "cfg": 7.5}',
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/prompts/",
        json=prompt_data,
        headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
    )

    if response.status_code == 201:
        data = response.json()
        prompt_id = data.get("id")
        print(f"✅ Prompt created successfully!")
        print(f"   ID: {prompt_id}")
        print(f"   Text: {data.get('text')}")
        print(f"   Negative Prompt: {data.get('negative_prompt')}")
        print(f"   Parameters: {data.get('parameters')}")
        print(f"   Rating: {data.get('rating')}")
        print(f"   Notes: {data.get('notes')}")
        return prompt_id
    else:
        print(f"❌ Failed to create prompt: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_read_prompt(prompt_id, token):
    """Test reading a prompt with new fields"""
    print_section("3. Testing READ with New Fields")

    response = requests.get(
        f"{BASE_URL}/api/v1/prompts/{prompt_id}",
        headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Prompt retrieved successfully!")
        print(f"   ID: {data.get('id')}")
        print(f"   Text: {data.get('text')[:50]}...")
        print(f"   Negative Prompt: {data.get('negative_prompt')}")
        print(f"   Parameters: {data.get('parameters')}")
        print(f"   Rating: {data.get('rating')}")
        print(f"   Notes: {data.get('notes')}")
        print(f"   Created by: {data.get('created_by')}")
        return True
    else:
        print(f"❌ Failed to read prompt: {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def test_update_prompt(prompt_id, token):
    """Test updating a prompt with new fields"""
    print_section("4. Testing UPDATE with New Fields")

    update_data = {
        "text": "Updated prompt text",
        "negative_prompt": "updated negative prompt",
        "parameters": '{"steps": 100, "cfg": 8.0}',
        "rating": 5,
        "notes": "Updated notes",
    }

    response = requests.put(
        f"{BASE_URL}/api/v1/prompts/{prompt_id}",
        json=update_data,
        headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Prompt updated successfully!")
        print(f"   ID: {data.get('id')}")
        print(f"   Updated Text: {data.get('text')[:50]}...")
        print(f"   Updated Negative Prompt: {data.get('negative_prompt')}")
        print(f"   Updated Parameters: {data.get('parameters')}")
        print(f"   Updated Rating: {data.get('rating')}")
        print(f"   Updated Notes: {data.get('notes')}")
        return True
    else:
        print(f"❌ Failed to update prompt: {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def test_search_my_prompts(token):
    """Test searching with my_prompts filter"""
    print_section("5. Testing Search with my_prompts Filter")

    # Search with my_prompts=true
    response = requests.get(
        f"{BASE_URL}/api/v1/search/complex",
        params={"my_prompts": True, "limit": 10},
        headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
    )

    if response.status_code == 200:
        data = response.json()
        total = data.get("total", 0)
        results = data.get("results", [])
        print(f"✅ Search with my_prompts successful!")
        print(f"   Total results: {total}")
        print(f"   Returned: {len(results)} prompts")

        if results:
            print(f"\n   First result:")
            first = results[0]
            print(f"   - ID: {first.get('id')}")
            print(f"   - Text: {first.get('original_prompt')[:50]}...")

        return True
    else:
        print(f"❌ Search failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def test_delete_prompt(prompt_id, token):
    """Test deleting a prompt"""
    print_section("6. Testing DELETE")

    response = requests.delete(
        f"{BASE_URL}/api/v1/prompts/{prompt_id}",
        headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
    )

    if response.status_code == 204:
        print(f"✅ Prompt deleted successfully!")
        return True
    else:
        print(f"❌ Failed to delete prompt: {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def main():
    print("=" * 60)
    print("  API Testing Suite - New Fields & My Prompts Filter")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")

    # Test 1: Authentication
    token = test_auth()
    if not token:
        print("\n❌ Cannot continue without authentication")
        return

    # Test 2: Create prompt with new fields
    prompt_id = test_create_prompt(token)
    if not prompt_id:
        print("\n❌ Cannot continue without created prompt")
        return

    # Test 3: Read prompt
    if not test_read_prompt(prompt_id, token):
        print("\n⚠️  Read test failed, but continuing...")

    # Test 4: Update prompt
    if not test_update_prompt(prompt_id, token):
        print("\n⚠️  Update test failed, but continuing...")

    # Test 5: Search with my_prompts
    if not test_search_my_prompts(token):
        print("\n⚠️  Search test failed, but continuing...")

    # Test 6: Delete prompt (cleanup)
    if not test_delete_prompt(prompt_id, token):
        print("\n⚠️  Delete test failed - you may need to clean up manually")

    print("\n" + "=" * 60)
    print("  Tests Completed!")
    print("=" * 60)
    print("\n✅ All tests executed. Check results above.")


if __name__ == "__main__":
    main()
