"""
Admin Router

Administrative and statistics endpoints.
"""

from fastapi import APIRouter, Depends
import sqlite3
from datetime import datetime

from ..auth import verify_token, optional_auth
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
    db: sqlite3.Connection = Depends(get_catalog_db),
    auth: dict = Depends(optional_auth),
):
    """
    Get database statistics (public).
    """
    stats = {}

    # Total prompts
    stats["total_prompts"] = db.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]

    # NSFW distribution
    stats["nsfw_distribution"] = {}
    for row in db.execute("SELECT level, COUNT(*) FROM nsfw_content GROUP BY level"):
        stats["nsfw_distribution"][row[0]] = row[1]

    # Top tags
    stats["top_tags"] = []
    for row in db.execute(
        """
        SELECT tag, COUNT(*) as count 
        FROM main_tags 
        GROUP BY tag 
        ORDER BY count DESC 
        LIMIT 200
    """
    ):
        stats["top_tags"].append({"tag": row[0], "count": row[1]})

    # All art styles (no limit)
    stats["top_art_styles"] = []
    for row in db.execute(
        """
        SELECT primary_style, COUNT(*) as count 
        FROM art_styles 
        WHERE primary_style IS NOT NULL
        GROUP BY primary_style 
        ORDER BY count DESC
    """
    ):
        stats["top_art_styles"].append({"style": row[0], "count": row[1]})
    
    # Total unique art styles count
    stats["total_art_styles"] = len(db.execute(
        """
        SELECT DISTINCT primary_style 
        FROM art_styles 
        WHERE primary_style IS NOT NULL
    """
    ).fetchall())
    
    # Total unique tags count
    stats["total_tags"] = len(db.execute(
        """
        SELECT DISTINCT tag 
        FROM main_tags
    """
    ).fetchall())

    # Character distribution
    stats["character_distribution"] = {}
    for row in db.execute(
        """
        SELECT number_of_people, COUNT(*) 
        FROM characters 
        GROUP BY number_of_people
    """
    ):
        stats["character_distribution"][str(row[0])] = row[1]

    return stats


@router.get("/filters")
async def get_filters(
    db: sqlite3.Connection = Depends(get_catalog_db),
    auth: dict = Depends(optional_auth),
):
    """
    Get available filter values from database (public).
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
