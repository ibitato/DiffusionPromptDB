"""
Search Router

Advanced search operations across catalog.
"""

from fastapi import APIRouter, Depends, Query
import sqlite3
from pathlib import Path
from typing import Optional

from ..auth import verify_api_key
from ..config import settings
from .catalog import get_catalog_db

router = APIRouter()


@router.get("/complex")
async def complex_search(
    text: Optional[str] = Query(None),
    nsfw_level: Optional[str] = Query(None),
    number_of_people: Optional[int] = Query(None),
    art_style: Optional[str] = Query(None),
    indoor_outdoor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_catalog_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Complex search with multiple filters including text search.
    
    Text search looks in original_prompt field.

    Requires: API Key
    """
    query = "SELECT DISTINCT p.id, p.original_prompt FROM prompts p"
    joins = []
    conditions = []
    params = []

    # Text search in prompt content
    if text:
        conditions.append("p.original_prompt LIKE ?")
        params.append(f"%{text}%")

    if nsfw_level:
        joins.append("JOIN nsfw_content n ON p.id = n.prompt_id")
        conditions.append("n.level = ?")
        params.append(nsfw_level)

    if number_of_people is not None:
        joins.append("JOIN characters c ON p.id = c.prompt_id")
        conditions.append("c.number_of_people = ?")
        params.append(number_of_people)

    if art_style:
        joins.append("JOIN art_styles a ON p.id = a.prompt_id")
        conditions.append("a.primary_style LIKE ?")
        params.append(f"%{art_style}%")

    if indoor_outdoor:
        joins.append("JOIN settings s ON p.id = s.prompt_id")
        conditions.append("s.indoor_outdoor = ?")
        params.append(indoor_outdoor)

    if joins:
        query += " " + " ".join(joins)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += f" LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    # Get total count first (without LIMIT/OFFSET)
    count_query = query.replace("SELECT DISTINCT p.id, p.original_prompt", "SELECT COUNT(DISTINCT p.id)")
    # Remove LIMIT and OFFSET from count query
    count_params = params[:-2]  # Remove last 2 params (limit and offset)
    total_count = db.execute(count_query, count_params).fetchone()[0]
    
    # Get paginated results
    results = db.execute(query, params).fetchall()

    return {"total": total_count, "results": [dict(row) for row in results]}


@router.get("/tags/{tag}")
async def search_by_tag(
    tag: str,
    limit: int = Query(20, ge=1, le=100),
    db: sqlite3.Connection = Depends(get_catalog_db),
    api_key: str = Depends(verify_api_key),
):
    """Search prompts by tag."""
    results = db.execute(
        """
        SELECT DISTINCT p.id, p.original_prompt
        FROM prompts p
        JOIN main_tags t ON p.id = t.prompt_id
        WHERE t.tag LIKE ?
        LIMIT ?
    """,
        (f"%{tag}%", limit),
    ).fetchall()

    return {"total": len(results), "results": [dict(row) for row in results]}
