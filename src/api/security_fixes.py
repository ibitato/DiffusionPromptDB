#!/usr/bin/env python3
"""
Security fixes implementation script
Run this to apply critical security patches and check for vulnerabilities
"""

import os
import secrets
import json
from pathlib import Path
import sqlite3
import hashlib
import sys


def generate_secure_config():
    """Generate secure configuration for production"""

    print("🔐 Generating secure configuration...")

    # Generate secure JWT secret
    jwt_secret = secrets.token_urlsafe(32)

    # Generate API keys
    api_keys = [secrets.token_urlsafe(24) for _ in range(3)]

    # Create .env file for API
    env_content = f"""# SECURITY CONFIGURATION - PRODUCTION
# Generated automatically - DO NOT COMMIT TO VERSION CONTROL

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=false

# Database paths
PROMPTS_DB_PATH=database/prompts_catalog.db
CATALOG_DB_PATH=database/prompts_catalog.db

# Security - CRITICAL: Keep these secret!
JWT_SECRET_KEY={jwt_secret}
API_KEYS={json.dumps(api_keys)}
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440  # 24 hours

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=600

# CORS - Update with your production domain
CORS_ORIGINS=["https://yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true

# Logging
LOG_LEVEL=WARNING
LOG_FILE=api_production.log

# Environment
ENVIRONMENT=production
DEBUG=false
"""

    # Save API .env file
    api_env_path = Path("src/api/.env")
    with open(api_env_path, "w") as f:
        f.write(env_content)

    print(f"✅ API configuration saved to {api_env_path}")

    # Create frontend .env.production
    frontend_env_content = f"""# Frontend Production Configuration
# DO NOT COMMIT TO VERSION CONTROL

VITE_API_URL=https://api.yourdomain.com/api/v1
VITE_API_KEY={api_keys[0]}
"""

    frontend_env_path = Path("../../frontend/.env.production")
    frontend_env_path.parent.mkdir(exist_ok=True)
    with open(frontend_env_path, "w") as f:
        f.write(frontend_env_content)

    print(f"✅ Frontend configuration saved to {frontend_env_path}")

    # Display summary
    print("\n📋 Configuration Summary:")
    print(f"  JWT Secret: {jwt_secret[:20]}... (length: {len(jwt_secret)})")
    print(f"  API Keys generated: {len(api_keys)}")
    print(f"    - Frontend key: {api_keys[0][:20]}...")
    print(f"    - Backend key: {api_keys[1][:20]}...")
    print(f"    - Admin key: {api_keys[2][:20]}...")

    return {"jwt_secret": jwt_secret, "api_keys": api_keys}


def check_vulnerabilities():
    """Check for common security vulnerabilities"""

    print("\n🔍 Checking for vulnerabilities...")

    issues = {"critical": [], "high": [], "medium": [], "low": []}

    # Check Python files for hardcoded secrets
    python_files = list(Path("src").rglob("*.py"))

    for file in python_files:
        try:
            content = file.read_text()

            # Check for hardcoded passwords
            if "password" in content.lower():
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "password" in line.lower() and "=" in line and '"' in line:
                        if "example" not in line.lower() and "test" not in line.lower():
                            issues["critical"].append(
                                f"Hardcoded password in {file}:{i}"
                            )

            # Check for hardcoded secrets
            if "secret" in content.lower():
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "secret" in line.lower() and "=" in line and '"' in line:
                        if "your-secret-key" in line or "change-this" in line:
                            issues["critical"].append(
                                f"Default secret key in {file}:{i}"
                            )
                        elif "example" not in line.lower():
                            issues["high"].append(
                                f"Potential hardcoded secret in {file}:{i}"
                            )

            # Check for SQL injection vulnerabilities
            if "execute" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "execute" in line and 'f"' in line:
                        issues["high"].append(
                            f"Potential SQL injection (f-string) in {file}:{i}"
                        )
                    if "execute" in line and ".format(" in line:
                        issues["high"].append(
                            f"Potential SQL injection (format) in {file}:{i}"
                        )
                    if "execute" in line and " + " in line:
                        issues["high"].append(
                            f"Potential SQL injection (concatenation) in {file}:{i}"
                        )

            # Check for plain text password comparison
            if "password ==" in content or "== password" in content:
                issues["critical"].append(f"Plain text password comparison in {file}")

        except Exception as e:
            issues["low"].append(f"Could not check {file}: {e}")

    # Check TypeScript/JavaScript files
    ts_files = list(Path("frontend/src").rglob("*.ts")) + list(
        Path("frontend/src").rglob("*.tsx")
    )

    for file in ts_files:
        try:
            content = file.read_text()

            # Check for API keys in code
            if "api_key" in content.lower() or "apikey" in content.lower():
                if "demo-read-key" in content or "your-api-key" in content:
                    issues["high"].append(f"Hardcoded API key in {file}")

            # Check for localStorage usage with sensitive data
            if "localStorage.setItem" in content:
                if "token" in content or "password" in content:
                    issues["medium"].append(f"Sensitive data in localStorage in {file}")

            # Check for eval usage
            if "eval(" in content:
                issues["critical"].append(f"eval() usage detected in {file}")

        except Exception as e:
            issues["low"].append(f"Could not check {file}: {e}")

    return issues


def check_database_security():
    """Check database for security issues"""

    print("\n🗄️ Checking database security...")

    issues = []
    db_path = Path("src/api/database/prompts_catalog.db")

    if not db_path.exists():
        print(f"  ⚠️ Database not found at {db_path}")
        return issues

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check for users table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        )
        if cursor.fetchone():
            # Check for plain text passwords
            cursor.execute("SELECT COUNT(*) FROM users WHERE LENGTH(password) < 50;")
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append(
                    f"Found {count} users with potentially unhashed passwords"
                )

        conn.close()

    except Exception as e:
        issues.append(f"Database check error: {e}")

    return issues


def generate_password_hash_migration():
    """Generate migration script for password hashing"""

    print("\n📝 Generating password hash migration script...")

    migration_script = '''#!/usr/bin/env python3
"""
Migration script to hash existing plain text passwords
"""

import sqlite3
import bcrypt
from pathlib import Path

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def migrate_passwords():
    """Migrate plain text passwords to hashed versions"""
    
    db_path = Path('src/api/database/prompts_catalog.db')
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            print("Users table not found - creating...")
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        
        # Get all users with plain text passwords (length < 50 characters)
        cursor.execute("SELECT id, username, password FROM users WHERE LENGTH(password) < 50;")
        users = cursor.fetchall()
        
        if not users:
            print("No plain text passwords found")
            return
        
        print(f"Found {len(users)} users with plain text passwords")
        
        for user_id, username, password in users:
            hashed = hash_password(password)
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
            print(f"  ✅ Hashed password for user: {username}")
        
        conn.commit()
        print(f"\\n✅ Successfully migrated {len(users)} passwords")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_passwords()
'''

    migration_path = Path("src/api/migrate_passwords.py")
    with open(migration_path, "w") as f:
        f.write(migration_script)

    print(f"✅ Migration script saved to {migration_path}")
    print("  Run with: python src/api/migrate_passwords.py")


def display_report(issues):
    """Display security report"""

    print("\n" + "=" * 60)
    print("🔒 SECURITY VULNERABILITY REPORT")
    print("=" * 60)

    total_issues = sum(len(v) for v in issues.values())

    if total_issues == 0:
        print("\n✅ No obvious vulnerabilities found!")
        print(
            "   Note: This is a basic check. Professional security audit recommended."
        )
    else:
        print(f"\n⚠️ Found {total_issues} potential security issues:\n")

        if issues["critical"]:
            print("🚨 CRITICAL Issues (Fix immediately!):")
            for issue in issues["critical"]:
                print(f"   - {issue}")
            print()

        if issues["high"]:
            print("⚠️ HIGH Priority Issues:")
            for issue in issues["high"]:
                print(f"   - {issue}")
            print()

        if issues["medium"]:
            print("⚡ MEDIUM Priority Issues:")
            for issue in issues["medium"]:
                print(f"   - {issue}")
            print()

        if issues["low"]:
            print("ℹ️ LOW Priority Issues:")
            for issue in issues["low"]:
                print(f"   - {issue}")
            print()

    print("\n" + "=" * 60)
    print("📋 RECOMMENDED ACTIONS:")
    print("=" * 60)
    print(
        """
1. ✅ Run this script to generate secure configuration
2. 📝 Review and run the password migration script
3. 🔐 Update all hardcoded secrets in the code
4. 🛡️ Implement HTTPS/TLS for production
5. 🔍 Use parameterized queries for all database operations
6. 🚫 Never commit .env files to version control
7. 📊 Set up monitoring and logging
8. 🔄 Regularly update dependencies
9. 👥 Implement proper RBAC (Role-Based Access Control)
10. 🔒 Enable all security headers in production
"""
    )


def main():
    """Main execution"""

    print("🔒 DiffusionPromptDB Security Audit & Fix Tool")
    print("=" * 60)

    # Check for vulnerabilities
    issues = check_vulnerabilities()

    # Check database security
    db_issues = check_database_security()
    if db_issues:
        issues["high"].extend(db_issues)

    # Display report
    display_report(issues)

    # Ask user if they want to generate secure config
    print("\n" + "=" * 60)
    response = input("Generate secure configuration files? (y/n): ").lower()

    if response == "y":
        config = generate_secure_config()
        generate_password_hash_migration()

        print("\n" + "=" * 60)
        print("✅ SECURITY FIXES APPLIED")
        print("=" * 60)
        print(
            """
Next steps:
1. Review the generated .env files
2. Run the password migration: python src/api/migrate_passwords.py
3. Update your deployment configuration
4. Never commit .env files to version control
5. Test thoroughly before production deployment
"""
        )

        # Create .gitignore entries
        gitignore_additions = """
# Security - Never commit these
.env
.env.production
.env.local
*.key
*.pem
*.crt
"""
        print("\n📝 Add these to your .gitignore:")
        print(gitignore_additions)
    else:
        print("\n⚠️ Configuration not generated. Please fix security issues manually.")

    print("\n🔗 For more details, see SECURITY_AUDIT_REPORT.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
