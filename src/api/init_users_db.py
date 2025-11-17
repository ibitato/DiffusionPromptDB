"""Initialize users database"""

import sqlite3
from pathlib import Path
from datetime import datetime

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create users database
db_path = Path("../data/users.db")
db_path.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create users table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) DEFAULT 'user',
    full_name TEXT,
    avatar_url TEXT,
    location TEXT,
    language TEXT DEFAULT 'en',
    default_landing_page TEXT DEFAULT 'dashboard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    must_change_password BOOLEAN DEFAULT 0,
    password_last_changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS user_password_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    password_hash TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS account_deletion_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    email TEXT,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dump_path TEXT,
    reason TEXT
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS user_verification_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
)
"""
)

# Create demo users with bcrypt passwords
DEMO_PASSWORD = "1302Quiter@#"
demo_users = [
    ("test", "test@example.com", DEMO_PASSWORD, "user"),
    ("admin", "admin@example.com", DEMO_PASSWORD, "admin"),
    ("user", "user@example.com", DEMO_PASSWORD, "user"),
]

for username, email, plain, role in demo_users:
    hashed = pwd_context.hash(plain)
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (username, email, password_hash, role, password_last_changed)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, email, hashed, role, datetime.utcnow().isoformat()),
    )
    cursor.execute(
        """
        INSERT INTO user_password_history (user_id, password_hash, changed_at)
        SELECT id, ?, ?
        FROM users WHERE username = ?
        ON CONFLICT DO NOTHING
        """,
        (hashed, datetime.utcnow().isoformat(), username),
    )

conn.commit()
conn.close()

print("✅ Users database initialized with secure demo accounts")
