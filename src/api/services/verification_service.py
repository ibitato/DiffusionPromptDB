"""
Email verification token management.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Tuple

from fastapi import HTTPException, status

from ..db import DatabaseConnection

TOKEN_TTL_HOURS = 24


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_verification_token(db: DatabaseConnection, user_id: int) -> Tuple[str, str]:
    """Create a verification token for a user."""
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)
    expires_at = (datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)).isoformat()

    db.execute("DELETE FROM user_verification_tokens WHERE user_id=?", (user_id,))
    db.execute(
        """
        INSERT INTO user_verification_tokens (user_id, token_hash, expires_at)
        VALUES (?, ?, ?)
        """,
        (user_id, token_hash, expires_at),
    )
    db.commit()
    return raw_token, expires_at


def consume_verification_token(db: DatabaseConnection, token: str) -> int:
    """Validate and consume a verification token, returning the user_id."""
    token_hash = _hash_token(token)
    row = db.execute(
        """
        SELECT user_id, expires_at
        FROM user_verification_tokens
        WHERE token_hash=?
        """,
        (token_hash,),
    ).fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or unknown token"
        )

    expires_at = row["expires_at"]
    if isinstance(expires_at, datetime):
        expiry = expires_at
    else:
        try:
            expiry = datetime.fromisoformat(str(expires_at))
        except ValueError:
            expiry = datetime.utcnow() - timedelta(seconds=1)

    if expiry < datetime.utcnow():
        db.execute("DELETE FROM user_verification_tokens WHERE token_hash=?", (token_hash,))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired"
        )

    user_id = row["user_id"]
    db.execute("DELETE FROM user_verification_tokens WHERE token_hash=?", (token_hash,))
    db.commit()
    return user_id
