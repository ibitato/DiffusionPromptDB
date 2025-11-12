"""
Catalog Router

Read operations for cataloged prompts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3
from pathlib import Path
import json

from ..models import CatalogResponse
from ..auth import verify_api_key
from ..config import settings

router = APIRouter()


def get_catalog_db():
    """Get catalog database connection."""
    db_path = Path(settings.catalog_db_path)
    if not db_path.exists():
        raise HTTPException(status_code=503, detail="Catalog database not available")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@router.get("/{prompt_id}")
async def get_cataloged_prompt(
    prompt_id: int,
    db: sqlite3.Connection = Depends(get_catalog_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get cataloged prompt with all categories.
    
    Requires: API Key
    """
    # Get main prompt data
    prompt_row = db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    
    if not prompt_row:
        raise HTTPException(status_code=404, detail="Cataloged prompt not found")
    
    # Build response with categories
    # This is simplified - in production you'd query all related tables
    result = {
        "id": prompt_row["id"],
        "original_prompt": prompt_row["original_prompt"],
        "categories": {
            # Simplified - would need to query all category tables
            "nsfw_level": db.execute(
                "SELECT level FROM nsfw_content WHERE prompt_id = ?", (prompt_id,)
            ).fetchone()
        },
        "metadata": {
            "processed_at": prompt_row["processed_at"],
            "model_used": prompt_row["model_used"],
            "tokens_used": {
                "input": prompt_row["input_tokens"],
                "output": prompt_row["output_tokens"]
            }
        }
    }
    
    return result


@router.get("/search/nsfw/{level}")
async def search_by_nsfw(
    level: str,
    limit: int = Query(20, ge=1, le=100),
    db: sqlite3.Connection = Depends(get_catalog_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Search prompts by NSFW level.
    
    Requires: API Key
    """
    results = db.execute("""
        SELECT p.id, p.original_prompt
        FROM prompts p
        JOIN nsfw_content n ON p.id = n.prompt_id
        WHERE n.level = ?
        LIMIT ?
    """, (level, limit)).fetchall()
    
    return {
        "total": len(results),
        "results": [dict(row) for row in results]
    }


@router.get("/search/style/{style}")
async def search_by_style(
    style: str,
    limit: int = Query(20, ge=1, le=100),
    db: sqlite3.Connection = Depends(get_catalog_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Search prompts by art style.
    
    Requires: API Key
    """
    results = db.execute("""
        SELECT p.id, p.original_prompt, a.primary_style
        FROM prompts p
        JOIN art_styles a ON p.id = a.prompt_id
        WHERE a.primary_style LIKE ?
        LIMIT ?
    """, (f"%{style}%", limit)).fetchall()
    
    return {
        "total": len(results),
        "results": [dict(row) for row in results]
    }
