"""Initialize users database"""
import sqlite3
from pathlib import Path
import hashlib

def hash_password(password: str) -> str:
    """Simple hash for demo purposes."""
    return hashlib.sha256(password.encode()).hexdigest()

# Create users database
db_path = Path("../data/users.db")
db_path.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
""")

# Create test user: test/test
password_hash = hash_password("test")
cursor.execute("""
INSERT OR IGNORE INTO users (username, email, password_hash, role)
VALUES ('test', 'test@example.com', ?, 'user')
""", (password_hash,))

# Create admin user: admin/admin
admin_hash = hash_password("admin")
cursor.execute("""
INSERT OR IGNORE INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@example.com', ?, 'admin')
""", (admin_hash,))

conn.commit()
conn.close()

print("✅ Users database initialized")
print("✅ User created: test/test (role: user)")
print("✅ User created: admin/admin (role: admin)")
