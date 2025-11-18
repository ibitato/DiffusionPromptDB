"""
Admin Router

Administrative and statistics endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from datetime import datetime

from ..auth import optional_auth, verify_token
from .catalog import get_catalog_db

router = APIRouter()


@router.get("/health")
async def health_check(auth: dict = Depends(optional_auth)):
    """
    Health check endpoint (public).
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated": auth is not None,
    }


@router.get("/stats")
async def get_statistics(
    my_prompts_only: bool = False,
    db: sqlite3.Connection = Depends(get_catalog_db),
    auth: dict = Depends(verify_token),
):
    """
    Get database statistics.

    Requires a valid authenticated session (non-admin users allowed).
    """
    user_id = None
    if my_prompts_only:
        user_id = auth.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=403,
                detail="Authenticated user context required for personal statistics.",
            )

    filter_params = (user_id,) if my_prompts_only else ()
    filter_clause = " WHERE created_by = ?" if my_prompts_only else ""

    stats = {}

    # Total prompts
    stats["total_prompts"] = db.execute(
        f"SELECT COUNT(*) FROM prompts{filter_clause}", filter_params
    ).fetchone()[0]

    # NSFW distribution
    stats["nsfw_distribution"] = {}
    if my_prompts_only:
        nsfw_query = """
            SELECT nc.level, COUNT(*)
            FROM nsfw_content nc
            JOIN prompts p ON p.id = nc.prompt_id
            WHERE p.created_by = ?
            GROUP BY nc.level
        """
        nsfw_params = [user_id]
    else:
        nsfw_query = """
            SELECT level, COUNT(*)
            FROM nsfw_content
            GROUP BY level
        """
        nsfw_params = []
    for row in db.execute(nsfw_query, nsfw_params):
        stats["nsfw_distribution"][row[0]] = row[1]

    # Top tags
    stats["top_tags"] = []
    if my_prompts_only:
        top_tags_query = """
            SELECT mt.tag, COUNT(*) as count
            FROM main_tags mt
            JOIN prompts p ON p.id = mt.prompt_id
            WHERE p.created_by = ?
            GROUP BY mt.tag
            ORDER BY count DESC
            LIMIT 200
        """
        tag_params = [user_id]
    else:
        top_tags_query = """
            SELECT tag, COUNT(*) as count
            FROM main_tags
            GROUP BY tag
            ORDER BY count DESC
            LIMIT 200
        """
        tag_params = []
    for row in db.execute(top_tags_query, tag_params):
        stats["top_tags"].append({"tag": row[0], "count": row[1]})

    # All art styles (no limit)
    stats["top_art_styles"] = []
    if my_prompts_only:
        art_styles_query = """
            SELECT ast.primary_style, COUNT(*) as count
            FROM art_styles ast
            JOIN prompts p ON p.id = ast.prompt_id
            WHERE ast.primary_style IS NOT NULL
              AND p.created_by = ?
            GROUP BY ast.primary_style
            ORDER BY count DESC
        """
        art_style_params = [user_id]
    else:
        art_styles_query = """
            SELECT primary_style, COUNT(*) as count
            FROM art_styles
            WHERE primary_style IS NOT NULL
            GROUP BY primary_style
            ORDER BY count DESC
        """
        art_style_params = []
    for row in db.execute(art_styles_query, art_style_params):
        stats["top_art_styles"].append({"style": row[0], "count": row[1]})

    # Total unique art styles count
    total_art_params = []
    if my_prompts_only:
        total_arts_query = """
            SELECT COUNT(DISTINCT ast.primary_style)
            FROM art_styles ast
            JOIN prompts p ON p.id = ast.prompt_id
            WHERE ast.primary_style IS NOT NULL
              AND p.created_by = ?
        """
        total_art_params.append(user_id)
    else:
        total_arts_query = """
            SELECT COUNT(DISTINCT primary_style)
            FROM art_styles
            WHERE primary_style IS NOT NULL
        """
    stats["total_art_styles"] = db.execute(total_arts_query, total_art_params).fetchone()[0]

    # Total unique tags count
    if my_prompts_only:
        total_tags_query = """
            SELECT COUNT(DISTINCT mt.tag)
            FROM main_tags mt
            JOIN prompts p ON p.id = mt.prompt_id
            WHERE p.created_by = ?
        """
        total_tag_params = [user_id]
    else:
        total_tags_query = "SELECT COUNT(DISTINCT tag) FROM main_tags"
        total_tag_params = []
    stats["total_tags"] = db.execute(total_tags_query, total_tag_params).fetchone()[0]

    # Character distribution
    stats["character_distribution"] = {}
    if my_prompts_only:
        characters_query = """
            SELECT ch.number_of_people, COUNT(*)
            FROM characters ch
            JOIN prompts p ON p.id = ch.prompt_id
            WHERE p.created_by = ?
            GROUP BY ch.number_of_people
        """
        character_params = [user_id]
    else:
        characters_query = """
            SELECT number_of_people, COUNT(*)
            FROM characters
            GROUP BY number_of_people
        """
        character_params = []
    for row in db.execute(characters_query, character_params):
        stats["character_distribution"][str(row[0])] = row[1]

    return stats


@router.get("/filters")
async def get_filters(
    db: sqlite3.Connection = Depends(get_catalog_db),
    _auth: dict = Depends(verify_token),
):
    """
    Get available filter values from database.
    Requires authentication but is accessible to any logged-in user.

    Returns unique values for NSFW levels and art styles with counts.
    """
    filters = {}

    # Get unique NSFW levels
    filters["nsfw_levels"] = []
    for row in db.execute(
        """
        SELECT DISTINCT level 
        FROM nsfw_content 
        WHERE level IS NOT NULL
        ORDER BY level
    """
    ):
        filters["nsfw_levels"].append(row[0])

    # Get all art styles with counts (ordered by count)
    filters["art_styles"] = []
    for row in db.execute(
        """
        SELECT primary_style, COUNT(*) as count 
        FROM art_styles 
        WHERE primary_style IS NOT NULL
        GROUP BY primary_style 
        ORDER BY count DESC
    """
    ):
        filters["art_styles"].append({"style": row[0], "count": row[1]})

    return filters
