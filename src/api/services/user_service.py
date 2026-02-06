"""
User service utilities for authentication, profiles, and password policies.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Mapping
import hashlib
import bcrypt

from fastapi import HTTPException, status
from passlib.context import CryptContext

from ..config import settings
from ..db import DatabaseConnection


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _row_to_user(row: Mapping[str, Any] | None) -> Dict[str, Any]:
    return dict(row) if row else {}


def _to_iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def get_user_by_username(
    db: DatabaseConnection, username: str
) -> Optional[Dict[str, Any]]:
    cursor = db.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    return _row_to_user(row) if row else None


def get_user_by_id(db: DatabaseConnection, user_id: int) -> Optional[Dict[str, Any]]:
    cursor = db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return _row_to_user(row) if row else None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password with backward compatibility for legacy SHA256 hashes.
    """
    if hashed_password.startswith("$2"):
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )

    if len(hashed_password) == 64:
        digest = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        return digest == hashed_password

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Password hash format is not supported.",
    )


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def enforce_password_policy(new_password: str):
    min_len = settings.password_min_length
    if len(new_password) < min_len:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must be at least {min_len} characters",
        )
    checks = [
        (any(c.islower() for c in new_password), "one lowercase letter"),
        (any(c.isupper() for c in new_password), "one uppercase letter"),
        (any(c.isdigit() for c in new_password), "one number"),
        (any(not c.isalnum() for c in new_password), "one symbol"),
    ]
    missing = [msg for ok, msg in checks if not ok]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must include {', '.join(missing)}",
        )


def assert_not_reused(db: DatabaseConnection, user_id: int, new_password: str):
    limit = settings.password_history_limit
    cursor = db.execute(
        """
        SELECT password_hash FROM user_password_history
        WHERE user_id = ?
        ORDER BY changed_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    for (old_hash,) in cursor.fetchall():
        if pwd_context.verify(new_password, old_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot reuse a recent password",
            )


def update_password(db: DatabaseConnection, user_id: int, new_password: str):
    enforce_password_policy(new_password)
    assert_not_reused(db, user_id, new_password)
    new_hash = pwd_context.hash(new_password)
    timestamp = datetime.utcnow().isoformat()
    db.execute(
        """
        UPDATE users
        SET password_hash=?, password_last_changed=?, must_change_password=?
        WHERE id=?
        """,
        (new_hash, timestamp, False, user_id),
    )
    db.execute(
        "INSERT INTO user_password_history (user_id, password_hash, changed_at) VALUES (?, ?, ?)",
        (user_id, new_hash, timestamp),
    )
    db.commit()


def needs_password_rotation(user: Dict[str, Any]) -> bool:
    last_changed = user.get("password_last_changed")
    if not last_changed:
        return True
    try:
        last_dt = datetime.fromisoformat(
            last_changed if isinstance(last_changed, str) else str(last_changed)
        )
    except ValueError:
        return True
    days = settings.password_rotation_days
    return datetime.utcnow() - last_dt > timedelta(days=days)


def serialize_profile(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "full_name": user.get("full_name"),
        "avatar_url": user.get("avatar_url"),
        "location": user.get("location"),
        "language": user.get("language") or "en",
        "default_landing_page": user.get("default_landing_page") or "dashboard",
        "must_change_password": bool(user.get("must_change_password")),
        "password_last_changed": _to_iso(user.get("password_last_changed")),
        "created_at": _to_iso(user.get("created_at")),
        "last_login": _to_iso(user.get("last_login")),
        "is_active": bool(user.get("is_active", 1)),
    }


def list_users(db: DatabaseConnection) -> List[Dict[str, Any]]:
    cursor = db.execute(
        "SELECT id, username, email, role, is_active, created_at, last_login, default_landing_page FROM users ORDER BY created_at DESC"
    )
    results = []
    for row in cursor.fetchall():
        results.append(
            {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "role": row["role"],
                "is_active": bool(row["is_active"]),
                "created_at": _to_iso(row["created_at"]),
                "last_login": _to_iso(row["last_login"]),
                "default_landing_page": row["default_landing_page"],
            }
        )
    return results
