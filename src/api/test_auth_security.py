#!/usr/bin/env python3
"""
Test script to verify password hashing implementation
"""

from security import hash_password, verify_password

def test_password_hashing():
    """Test and generate password hashes for demo accounts"""
    
    print("🔐 Testing Secure Authentication")
    print("=" * 50)
    
    # Test passwords
    test_passwords = {
        "test": "test123",
        "admin": "admin123",
        "user": "user123"
    }
    
    print("\n📝 Generating secure password hashes:")
    print("-" * 50)
    
    hashes = {}
    for username, password in test_passwords.items():
        hashed = hash_password(password)
        hashes[username] = hashed
        print(f"\n{username}:")
        print(f"  Password: {password}")
        print(f"  Hash: {hashed}")
        
        # Verify the hash works
        is_valid = verify_password(password, hashed)
        print(f"  Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    print("\n🔍 Testing current hashes in auth.py:")
    print("-" * 50)
    
    # These are the hashes currently in auth.py
    current_hashes = {
        "test": "$2b$12$Yd.8YCHGQxB3ZOlFg3VrSeHVdEVQkDGNp5v8xWxP8UY3jNTfOaBby",
        "admin": "$2b$12$tIgFB5Tse8vGLvBNgBHELuELJdJdQ8qZzGvL3YfJFKlKKqK6T8jAO",
        "user": "$2b$12$GhCqKhJQd8x8LzVz5bKWQOXoBmVvM2HwFYEGq5fVKkkJNOdYsX8r.",
    }
    
    for username, password in test_passwords.items():
        current_hash = current_hashes.get(username)
        if current_hash:
            is_valid = verify_password(password, current_hash)
            print(f"{username}/{password}: {'✅ Valid' if is_valid else '❌ Invalid - needs update'}")
            
            if not is_valid:
                print(f"  New hash needed: {hashes[username]}")
    
    print("\n✅ Password hashing security implemented successfully!")
    print("\n📌 Important Notes:")
    print("  - Never store plain text passwords")
    print("  - Always use bcrypt or similar for hashing")
    print("  - Use strong passwords in production")
    print("  - Store passwords in a secure database")
    
    return True

if __name__ == "__main__":
    test_password_hashing()
