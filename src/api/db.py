"""
Shared database helpers.

Provides reusable dependency functions for SQLite connections.
"""

from pathlib import Path
import sqlite3
from fastapi import HTTPException, status

from .config import settings


def _open_sqlite(path: Path) -> sqlite3.Connection:
    """Return SQLite connection with row factory."""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_users_db():
    """FastAPI dependency that yields a connection to users database."""
    raw_path = settings.users_db_path or "../data/users.db"
    db_path = Path(raw_path).expanduser().resolve()
    if not db_path.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Users database not available",
        )
    conn = _open_sqlite(db_path)
    try:
        yield conn
    finally:
        conn.close()


def get_prompts_db_connection():
    """Return connection (not dependency) to prompts catalog DB."""
    raw_path = settings.prompts_db_path
    db_path = Path(raw_path).expanduser().resolve()
    if not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return _open_sqlite(db_path)
