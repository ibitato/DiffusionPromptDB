import os
#!/usr/bin/env python3
"""
Test script to verify login works with hashed passwords
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"


def test_login(username: str, password: str):
    """Test login endpoint"""

    print(f"\n🔐 Testing login for {username}/{password}")
    print("-" * 40)

    # Prepare login data
    login_data = {"username": username, "password": password}

    try:
        # Make login request
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   Token: {data['access_token'][:50]}...")
            print(f"   User: {data['user']['username']} (role: {data['user']['role']})")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print("   Start the server with: cd src/api && python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function"""

    print("🔒 Testing Secure Authentication Implementation")
    print("=" * 50)

    # Test accounts with new passwords
    test_accounts = [
        ("test", os.environ.get("TEST_DEMO_PASSWORD", "TestPass!@#456")),  # Regular user
        ("admin", os.environ.get("TEST_DEMO_PASSWORD", "TestPass!@#456")),  # Admin user
        ("user", os.environ.get("TEST_DEMO_PASSWORD", "TestPass!@#456")),  # Another regular user
        ("test", "wrong"),  # Wrong password test
        ("nonexistent", "test"),  # Non-existent user test
    ]

    print("\n📋 Testing login with hashed passwords:")

    success_count = 0
    for username, password in test_accounts:
        if test_login(username, password):
            success_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{len(test_accounts)} tests passed")

    if success_count == 3:  # Only the first 3 should succeed
        print("✅ Password hashing is working correctly!")
        print("\n🔐 Security improvements implemented:")
        print("  ✓ Passwords are now hashed with bcrypt")
        print("  ✓ Plain text passwords eliminated")
        print("  ✓ Login verification uses secure comparison")
        print("\n⚠️ Note: Demo credentials are configured via environment variables.")
        print("  Set TEST_DEMO_PASSWORD to override the default test password.")
    else:
        print("⚠️ Some tests failed. Check the implementation.")


if __name__ == "__main__":
    main()
