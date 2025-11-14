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
    tags: Optional[str] = Query(None, description="Comma-separated tags to search for"),
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
    Complex search with multiple filters including text and tags search.
    
    Text search looks in original_prompt field.
    Tags can be comma-separated for multiple tag search.

    Requires: API Key
    """
    # Modified to return full data including tags, nsfw_level, art_style
    # Using the actual database structure
    query = """
        SELECT DISTINCT 
            p.id, 
            p.original_prompt,
            nc.level as nsfw_level,
            ast.primary_style as art_style,
            ch.number_of_people,
            GROUP_CONCAT(DISTINCT mt.tag) as tags
        FROM prompts p
        LEFT JOIN nsfw_content nc ON p.id = nc.prompt_id
        LEFT JOIN art_styles ast ON p.id = ast.prompt_id
        LEFT JOIN characters ch ON p.id = ch.prompt_id
        LEFT JOIN main_tags mt ON p.id = mt.prompt_id
    """
    joins = []
    conditions = []
    params = []

    # Text search in prompt content
    if text:
        conditions.append("p.original_prompt LIKE ?")
        params.append(f"%{text}%")
    
    # Tags search - can be multiple tags separated by comma
    if tags:
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        for i, tag in enumerate(tag_list):
            alias = f"tf{i}"  # Changed alias to avoid conflict with left join
            joins.append(f"INNER JOIN main_tags {alias} ON p.id = {alias}.prompt_id")
            conditions.append(f"{alias}.tag LIKE ?")
            params.append(f"%{tag}%")

    if nsfw_level:
        conditions.append("nc.level = ?")
        params.append(nsfw_level)

    if number_of_people is not None:
        conditions.append("ch.number_of_people = ?")
        params.append(number_of_people)

    if art_style:
        conditions.append("ast.primary_style LIKE ?")
        params.append(f"%{art_style}%")

    if indoor_outdoor:
        joins.append("INNER JOIN settings s ON p.id = s.prompt_id")
        conditions.append("s.indoor_outdoor = ?")
        params.append(indoor_outdoor)

    if joins:
        query += " " + " ".join(joins)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    # Add GROUP BY for aggregation
    query += " GROUP BY p.id, p.original_prompt, nc.level, ast.primary_style, ch.number_of_people"

    # Get total count first - need to include necessary LEFT JOINs
    count_query = f"""
        SELECT COUNT(DISTINCT p.id) 
        FROM prompts p
        LEFT JOIN nsfw_content nc ON p.id = nc.prompt_id
        LEFT JOIN art_styles ast ON p.id = ast.prompt_id
        LEFT JOIN characters ch ON p.id = ch.prompt_id
        LEFT JOIN main_tags mt ON p.id = mt.prompt_id
    """
    if joins:
        count_query += " " + " ".join(joins)
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    total_count = db.execute(count_query, params).fetchone()[0]
    
    # Add pagination to main query
    query += f" LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    # Get paginated results
    results = db.execute(query, params).fetchall()
    
    # Process results to format tags properly
    formatted_results = []
    for row in results:
        result = dict(row)
        # Convert comma-separated tags string to array
        if result.get('tags'):
            result['tags'] = result['tags'].split(',')
        else:
            result['tags'] = []
        formatted_results.append(result)

    return {"total": total_count, "results": formatted_results}


@router.get("/tags/{tag}")
async def search_by_tag(
    tag: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_catalog_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Search prompts by tag(s) with pagination.
    Multiple tags can be separated by comma (e.g. "nude,solo")
    """
    # Split tags by comma and clean whitespace
    tags = [t.strip() for t in tag.split(',') if t.strip()]
    
    if len(tags) == 1:
        # Single tag search - with full data
        query = """
            SELECT DISTINCT 
                p.id, 
                p.original_prompt,
                nc.level as nsfw_level,
                ast.primary_style as art_style,
                ch.number_of_people,
                GROUP_CONCAT(DISTINCT mt.tag) as tags
            FROM prompts p
            JOIN main_tags t ON p.id = t.prompt_id
            LEFT JOIN nsfw_content nc ON p.id = nc.prompt_id
            LEFT JOIN art_styles ast ON p.id = ast.prompt_id
            LEFT JOIN characters ch ON p.id = ch.prompt_id
            LEFT JOIN main_tags mt ON p.id = mt.prompt_id
            WHERE t.tag LIKE ?
            GROUP BY p.id, p.original_prompt, nc.level, ast.primary_style, ch.number_of_people
        """
        params = [f"%{tags[0]}%"]
        
        # Get total count
        count_query = query.replace("SELECT DISTINCT p.id, p.original_prompt", "SELECT COUNT(DISTINCT p.id)")
        total_count = db.execute(count_query, params).fetchone()[0]
        
        # Add pagination
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        results = db.execute(query, params).fetchall()
    else:
        # Multiple tags search - must have ALL tags (AND logic) - with full data
        query = """
            SELECT DISTINCT 
                p.id, 
                p.original_prompt,
                nc.level as nsfw_level,
                ast.primary_style as art_style,
                ch.number_of_people,
                GROUP_CONCAT(DISTINCT mt.tag) as tags
            FROM prompts p
        """
        for i in range(len(tags)):
            query += f" JOIN main_tags t{i} ON p.id = t{i}.prompt_id"
        
        query += """
            LEFT JOIN nsfw_content nc ON p.id = nc.prompt_id
            LEFT JOIN art_styles ast ON p.id = ast.prompt_id
            LEFT JOIN characters ch ON p.id = ch.prompt_id
            LEFT JOIN main_tags mt ON p.id = mt.prompt_id
        """
        
        conditions = [f"t{i}.tag LIKE ?" for i in range(len(tags))]
        query += " WHERE " + " AND ".join(conditions)
        query += " GROUP BY p.id, p.original_prompt, nc.level, ast.primary_style, ch.number_of_people"
        
        params = [f"%{t}%" for t in tags]
        
        # Get total count
        count_query = query.replace("SELECT DISTINCT p.id, p.original_prompt", "SELECT COUNT(DISTINCT p.id)")
        total_count = db.execute(count_query, params).fetchone()[0]
        
        # Add pagination
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        results = db.execute(query, params).fetchall()

    # Process results to format tags properly
    formatted_results = []
    for row in results:
        result = dict(row)
        # Convert comma-separated tags string to array
        if result.get('tags'):
            result['tags'] = result['tags'].split(',')
        else:
            result['tags'] = []
        formatted_results.append(result)

    return {"total": total_count, "results": formatted_results}
