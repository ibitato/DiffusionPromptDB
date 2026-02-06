"""
Catalog Router

Read operations for cataloged prompts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
import json

from ..models import CatalogResponse
from ..auth import verify_api_key
from ..db import DatabaseConnection, get_prompts_db

router = APIRouter()


def escape_like_pattern(text: str) -> str:
    """
    Escape special LIKE wildcards to prevent injection and overly broad searches.
    
    Escapes:
    - \ (backslash) -> \\
    - % (percent) -> \%
    - _ (underscore) -> \_
    
    Args:
        text: User input text for LIKE pattern
        
    Returns:
        Escaped text safe for LIKE queries
    """
    if not text:
        return text
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get("/{prompt_id}")
async def get_cataloged_prompt(
    prompt_id: int,
    db: DatabaseConnection = Depends(get_prompts_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Get cataloged prompt with all categories.

    Requires: API Key
    """
    # Get main prompt data
    prompt_row = db.execute(
        "SELECT * FROM prompts WHERE id = ?", (prompt_id,)
    ).fetchone()

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
                "output": prompt_row["output_tokens"],
            },
        },
    }

    return result


@router.get("/search/nsfw/{level}")
async def search_by_nsfw(
    level: str,
    limit: int = Query(20, ge=1, le=100),
    db: DatabaseConnection = Depends(get_prompts_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Search prompts by NSFW level.

    Requires: API Key
    """
    results = db.execute(
        """
        SELECT p.id, p.original_prompt
        FROM prompts p
        JOIN nsfw_content n ON p.id = n.prompt_id
        WHERE n.level = ?
        LIMIT ?
    """,
        (level, limit),
    ).fetchall()

    return {"total": len(results), "results": [dict(row) for row in results]}


@router.get("/search/style/{style}")
async def search_by_style(
    style: str,
    limit: int = Query(20, ge=1, le=100),
    db: DatabaseConnection = Depends(get_prompts_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Search prompts by art style (with LIKE pattern escaping).

    Requires: API Key
    """
    # Escape wildcards to prevent LIKE injection
    safe_style = escape_like_pattern(style)

    results = db.execute(
        """
        SELECT p.id, p.original_prompt, a.primary_style
        FROM prompts p
        JOIN art_styles a ON p.id = a.prompt_id
        WHERE a.primary_style LIKE ?
        LIMIT ?
    """,
        (f"%{safe_style}%", limit),
    ).fetchall()

    return {"total": len(results), "results": [dict(row) for row in results]}
