import os
"""
Utility script to upgrade users.db with profile + security fields.

Run: `python -m src.api.migrations.update_users_schema`
"""

import sqlite3
from pathlib import Path
from datetime import datetime

from passlib.context import CryptContext

BASE_DIR = Path(__file__).resolve().parents[2]
USERS_DB = BASE_DIR / "data" / "users.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def ensure_column(cursor, table, column, col_type, default=None):
    added = False
    if not column_exists(cursor, table, column):
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        added = True
    if default is not None and added:
        cursor.execute(f"UPDATE {table} SET {column}=? WHERE {column} IS NULL", (default,))


def ensure_table(cursor, name, ddl):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    )
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(ddl)


def upgrade():
    if not USERS_DB.exists():
        raise SystemExit(f"users.db not found at {USERS_DB}")

    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()

    ensure_column(cursor, "users", "full_name", "TEXT")
    ensure_column(cursor, "users", "avatar_url", "TEXT")
    ensure_column(cursor, "users", "location", "TEXT")
    ensure_column(cursor, "users", "language", "TEXT", "en")
    ensure_column(cursor, "users", "default_landing_page", "TEXT", "dashboard")
    ensure_column(cursor, "users", "must_change_password", "INTEGER", 0)
    ensure_column(cursor, "users", "password_last_changed", "TIMESTAMP", datetime.utcnow().isoformat())

    ensure_table(
        cursor,
        "user_password_history",
        """
        CREATE TABLE user_password_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            password_hash TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
    )

    ensure_table(
        cursor,
        "account_deletion_audit",
        """
        CREATE TABLE account_deletion_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            email TEXT,
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dump_path TEXT,
            reason TEXT
        )
        """,
    )

    ensure_table(
        cursor,
        "user_verification_tokens",
        """
        CREATE TABLE user_verification_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
    )

    # Upgrade default demo accounts to bcrypt hashes if they still use SHA
    cursor.execute("SELECT id, username, password_hash FROM users")
    for user_id, username, password_hash in cursor.fetchall():
        if password_hash and password_hash.startswith("$2b$"):
            continue  # Already bcrypt
        plain = None
        if username in {"test", "admin", "user"}:
            plain = os.environ.get("DEMO_PASSWORD", "ChangeMeNow!1")
        if plain:
            new_hash = pwd_context.hash(plain)
            cursor.execute(
                "UPDATE users SET password_hash=?, must_change_password=0, password_last_changed=? WHERE id=?",
                (new_hash, datetime.utcnow().isoformat(), user_id),
            )
            cursor.execute(
                "INSERT INTO user_password_history (user_id, password_hash, changed_at) VALUES (?, ?, ?)",
                (user_id, new_hash, datetime.utcnow().isoformat()),
            )
        else:
            # Require password reset for unknown credentials
            cursor.execute(
                "UPDATE users SET must_change_password=1 WHERE id=?", (user_id,)
            )

    conn.commit()
    conn.close()
    print("✅ users.db upgraded successfully.")


if __name__ == "__main__":
    upgrade()
