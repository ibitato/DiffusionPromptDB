"""
Account lifecycle helpers (profile updates, deletion dumps, etc.).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import HTTPException, status

from ..db import DatabaseConnection, get_prompts_db_connection

DUMP_DIR = Path(__file__).resolve().parents[2] / "data" / "account_dumps"


def dump_user_snapshot(
    user: Dict[str, Any],
    users_db: DatabaseConnection,
) -> str:
    """Persist user data prior to deletion."""
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    dump_path = DUMP_DIR / f"user_{user['id']}_{timestamp}.json"

    snapshot: Dict[str, Any] = {"user": user}

    # Preferences
    cursor = users_db.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?", (user["id"],)
    )
    row = cursor.fetchone()
    snapshot["preferences"] = dict(row) if row else None

    # Prompts created by user
    prompts_conn = get_prompts_db_connection()
    try:
        cursor = prompts_conn.execute(
            "SELECT * FROM prompts WHERE created_by = ?", (user["id"],)
        )
        snapshot["prompts"] = [dict(r) for r in cursor.fetchall()]
    finally:
        prompts_conn.close()

    dump_path.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")
    return str(dump_path.resolve())


def delete_user_account(
    user: Dict[str, Any],
    users_db: DatabaseConnection,
    reason: str = "",
):
    """Remove user and related data after dumping snapshot."""
    dump_path = dump_user_snapshot(user, users_db)

    prompts_conn = get_prompts_db_connection()
    try:
        prompts_conn.execute("DELETE FROM prompts WHERE created_by = ?", (user["id"],))
        prompts_conn.commit()
    finally:
        prompts_conn.close()

    users_db.execute("DELETE FROM user_preferences WHERE user_id=?", (user["id"],))
    users_db.execute("DELETE FROM user_password_history WHERE user_id=?", (user["id"],))
    users_db.execute("DELETE FROM users WHERE id=?", (user["id"],))
    users_db.execute(
        """
        INSERT INTO account_deletion_audit (user_id, username, email, dump_path, reason)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user["id"], user["username"], user["email"], dump_path, reason),
    )
    users_db.commit()

    return dump_path
