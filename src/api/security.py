"""
Security utilities for password hashing and verification

This module provides secure password hashing using bcrypt.
"""

import bcrypt
import secrets
import string


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    # Encode password to bytes and hash it
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Return as string for storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Encode both passwords to bytes for comparison
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a secure random password.
    
    Args:
        length: Length of the password (default: 16)
        
    Returns:
        Secure random password string
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def is_password_strong(password: str) -> tuple[bool, str]:
    """
    Check if a password meets minimum security requirements.
    
    Args:
        password: Password to check
        
    Returns:
        Tuple of (is_strong, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"


# Test the functions
if __name__ == "__main__":
    print("🔐 Testing Password Security Module")
    print("-" * 40)
    
    # Test password hashing
    test_password = "MySecurePassword123!"
    print(f"Original password: {test_password}")
    
    hashed = hash_password(test_password)
    print(f"Hashed password: {hashed[:50]}...")
    print(f"Hash length: {len(hashed)}")
    
    # Test password verification
    is_valid = verify_password(test_password, hashed)
    print(f"Password verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    wrong_password = "WrongPassword"
    is_invalid = verify_password(wrong_password, hashed)
    print(f"Wrong password check: {'❌ Invalid' if not is_invalid else '✅ Valid'}")
    
    # Test password strength
    passwords_to_test = [
        "weak",
        "WeakPass",
        "StrongPass123!",
    ]
    
    print("\n🔍 Password Strength Tests:")
    for pwd in passwords_to_test:
        is_strong, msg = is_password_strong(pwd)
        print(f"  '{pwd}': {'✅' if is_strong else '❌'} - {msg}")
    
    # Generate secure password
    secure_pwd = generate_secure_password()
    print(f"\n🔑 Generated secure password: {secure_pwd}")
