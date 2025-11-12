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
        "authenticated": auth is not None
    }


@router.get("/stats")
async def get_statistics(
    db: sqlite3.Connection = Depends(get_catalog_db),
    auth: dict = Depends(optional_auth)
):
    """
    Get database statistics (public).
    """
    stats = {}
    
    # Total prompts
    stats['total_prompts'] = db.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    
    # NSFW distribution
    stats['nsfw_distribution'] = {}
    for row in db.execute("SELECT level, COUNT(*) FROM nsfw_content GROUP BY level"):
        stats['nsfw_distribution'][row[0]] = row[1]
    
    # Top tags
    stats['top_tags'] = []
    for row in db.execute("""
        SELECT tag, COUNT(*) as count 
        FROM main_tags 
        GROUP BY tag 
        ORDER BY count DESC 
        LIMIT 15
    """):
        stats['top_tags'].append({"tag": row[0], "count": row[1]})
    
    # Top art styles
    stats['top_art_styles'] = []
    for row in db.execute("""
        SELECT primary_style, COUNT(*) as count 
        FROM art_styles 
        WHERE primary_style IS NOT NULL
        GROUP BY primary_style 
        ORDER BY count DESC 
        LIMIT 10
    """):
        stats['top_art_styles'].append({"style": row[0], "count": row[1]})
    
    # Character distribution
    stats['character_distribution'] = {}
    for row in db.execute("""
        SELECT number_of_people, COUNT(*) 
        FROM characters 
        GROUP BY number_of_people
    """):
        stats['character_distribution'][str(row[0])] = row[1]
    
    return stats
