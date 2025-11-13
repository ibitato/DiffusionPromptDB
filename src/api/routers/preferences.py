"""
User Preferences Router

Endpoints for managing user preferences.
"""

from fastapi import APIRouter, Depends, HTTPException
import sqlite3
import json
from pathlib import Path

from ..auth import verify_token
from ..models.user_preferences_models import (
    UserPreferencesResponse,
    UserPreferencesUpdate,
)

router = APIRouter()


def get_users_db():
    """Get users database connection."""
    db_path = Path(__file__).parent.parent.parent / "data" / "users.db"
    if not db_path.exists():
        raise HTTPException(status_code=503, detail="Users database not available")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    db: sqlite3.Connection = Depends(get_users_db),
    auth: dict = Depends(verify_token),
):
    """
    Get user preferences.
    
    Requires: JWT Token
    """
    user_id = auth["user_id"]
    
    # Get or create preferences
    pref_row = db.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    
    if not pref_row:
        # Create default preferences
        default_excluded = json.dumps(["high quality", "masterpiece", "best quality"])
        db.execute(
            """
            INSERT INTO user_preferences (user_id, show_unspecified, excluded_tags)
            VALUES (?, 1, ?)
            """,
            (user_id, default_excluded)
        )
        db.commit()
        
        return UserPreferencesResponse(
            user_id=user_id,
            show_unspecified=True,
            excluded_tags=["high quality", "masterpiece", "best quality"]
        )
    
    # Parse excluded tags from JSON
    excluded_tags = json.loads(pref_row["excluded_tags"]) if pref_row["excluded_tags"] else []
    
    return UserPreferencesResponse(
        user_id=pref_row["user_id"],
        show_unspecified=bool(pref_row["show_unspecified"]),
        excluded_tags=excluded_tags
    )


@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_preferences(
    preferences: UserPreferencesUpdate,
    db: sqlite3.Connection = Depends(get_users_db),
    auth: dict = Depends(verify_token),
):
    """
    Update user preferences.
    
    Requires: JWT Token
    """
    user_id = auth["user_id"]
    
    # Get current preferences
    current = db.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    
    if not current:
        # Create new preferences
        show_unspec = preferences.show_unspecified if preferences.show_unspecified is not None else True
        excluded = preferences.excluded_tags if preferences.excluded_tags is not None else ["high quality", "masterpiece", "best quality"]
        
        db.execute(
            """
            INSERT INTO user_preferences (user_id, show_unspecified, excluded_tags)
            VALUES (?, ?, ?)
            """,
            (user_id, show_unspec, json.dumps(excluded))
        )
    else:
        # Update existing preferences
        show_unspec = preferences.show_unspecified if preferences.show_unspecified is not None else bool(current["show_unspecified"])
        
        if preferences.excluded_tags is not None:
            excluded = preferences.excluded_tags
        else:
            excluded = json.loads(current["excluded_tags"]) if current["excluded_tags"] else []
        
        db.execute(
            """
            UPDATE user_preferences 
            SET show_unspecified = ?, excluded_tags = ?
            WHERE user_id = ?
            """,
            (show_unspec, json.dumps(excluded), user_id)
        )
    
    db.commit()
    
    # Return updated preferences
    updated = db.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    
    excluded_tags = json.loads(updated["excluded_tags"]) if updated["excluded_tags"] else []
    
    return UserPreferencesResponse(
        user_id=updated["user_id"],
        show_unspecified=bool(updated["show_unspecified"]),
        excluded_tags=excluded_tags
    )
