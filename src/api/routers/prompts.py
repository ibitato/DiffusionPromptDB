"""
Prompts Router

CRUD operations for original prompts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
import sqlite3
from pathlib import Path

from ..models import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptListResponse
)
from ..auth import verify_api_key, verify_token
from ..config import settings

router = APIRouter()


def get_prompts_db():
    """Get database connection."""
    db_path = Path(settings.prompts_db_path)
    if not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@router.get("/", response_model=PromptListResponse)
async def list_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    db: sqlite3.Connection = Depends(get_prompts_db),
    api_key: str = Depends(verify_api_key)
):
    """
    List prompts with pagination.
    Uses catalog DB schema (original_prompt, processed_at).
    
    Requires: API Key
    """
    offset = (page - 1) * page_size
    
    # Catalog DB doesn't have category column, so ignore for now
    # Count total
    total = db.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    
    # Get results - map catalog fields to expected frontend fields
    query = """
        SELECT 
            p.id,
            p.original_prompt as text,
            p.model_used as model,
            p.processed_at as created_at,
            p.processed_at as updated_at,
            a.primary_style as category,
            NULL as negative_prompt,
            NULL as parameters,
            NULL as tags,
            NULL as rating,
            NULL as notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        ORDER BY p.processed_at DESC
        LIMIT ? OFFSET ?
    """
    params = (page_size, offset)
    
    # Get results
    results = db.execute(query, params).fetchall()
    
    prompts = [dict(row) for row in results]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": prompts
    }


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: int,
    db: sqlite3.Connection = Depends(get_prompts_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get a specific prompt by ID.
    Maps catalog schema to frontend expected schema.
    
    Requires: API Key
    """
    # Get prompt with mapped fields
    row = db.execute("""
        SELECT 
            p.id,
            p.original_prompt as text,
            p.model_used as model,
            p.processed_at as created_at,
            p.processed_at as updated_at,
            a.primary_style as category,
            NULL as negative_prompt,
            NULL as parameters,
            NULL as tags,
            NULL as rating,
            NULL as notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        WHERE p.id = ?
    """, (prompt_id,)).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return dict(row)


@router.post("/", response_model=PromptResponse, status_code=201)
async def create_prompt(
    prompt: PromptCreate,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token)
):
    """
    Create a new prompt in catalog DB.
    Only admin users can create prompts.
    
    Requires: JWT Token (write access)
    """
    from datetime import datetime
    
    # Get next ID
    max_id = db.execute("SELECT MAX(id) FROM prompts").fetchone()[0]
    next_id = (max_id or 0) + 1
    
    # Insert into prompts table (catalog schema)
    db.execute("""
        INSERT INTO prompts (id, original_prompt, processed_at, model_used, input_tokens, output_tokens)
        VALUES (?, ?, ?, ?, 0, 0)
    """, (
        next_id,
        prompt.text,
        datetime.utcnow().isoformat(),
        prompt.model or 'manual-entry'
    ))
    
    # Insert basic categorization
    db.execute("INSERT INTO characters (prompt_id, number_of_people, breast_size) VALUES (?, 1, 'unspecified')", (next_id,))
    db.execute("INSERT INTO nsfw_content (prompt_id, level) VALUES (?, 'safe')", (next_id,))
    
    if prompt.category:
        db.execute("INSERT INTO art_styles (prompt_id, primary_style) VALUES (?, ?)", (next_id, prompt.category))
    
    db.commit()
    
    # Return created prompt with mapping
    row = db.execute("""
        SELECT 
            p.id,
            p.original_prompt as text,
            p.model_used as model,
            p.processed_at as created_at,
            p.processed_at as updated_at,
            a.primary_style as category,
            NULL as negative_prompt,
            NULL as parameters,
            NULL as tags,
            NULL as rating,
            NULL as notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        WHERE p.id = ?
    """, (next_id,)).fetchone()
    
    return dict(row)


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt: PromptUpdate,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token)
):
    """
    Update an existing prompt in catalog DB.
    Updates prompt text and category (art_style).
    
    Requires: JWT Token (write access)
    """
    # Check if exists
    existing = db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Update prompt text
    if prompt.text is not None:
        db.execute("UPDATE prompts SET original_prompt = ? WHERE id = ?", (prompt.text, prompt_id))
    
    # Update model
    if prompt.model is not None:
        db.execute("UPDATE prompts SET model_used = ? WHERE id = ?", (prompt.model, prompt_id))
    
    # Update category (art_style)
    if prompt.category is not None:
        # Check if art_style entry exists
        exists = db.execute("SELECT 1 FROM art_styles WHERE prompt_id = ?", (prompt_id,)).fetchone()
        if exists:
            db.execute("UPDATE art_styles SET primary_style = ? WHERE prompt_id = ?", (prompt.category, prompt_id))
        else:
            db.execute("INSERT INTO art_styles (prompt_id, primary_style) VALUES (?, ?)", (prompt_id, prompt.category))
    
    db.commit()
    
    # Return updated prompt with mapping
    row = db.execute("""
        SELECT 
            p.id,
            p.original_prompt as text,
            p.model_used as model,
            p.processed_at as created_at,
            p.processed_at as updated_at,
            a.primary_style as category,
            NULL as negative_prompt,
            NULL as parameters,
            NULL as tags,
            NULL as rating,
            NULL as notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        WHERE p.id = ?
    """, (prompt_id,)).fetchone()
    
    return dict(row)


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(
    prompt_id: int,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token)
):
    """
    Delete a prompt from catalog DB.
    Cascades to all related tables.
    
    Requires: JWT Token (write access)
    """
    # Check if exists
    existing = db.execute("SELECT 1 FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Delete from all related tables (catalog schema has 20+ tables)
    tables = [
        "main_tags", "emotions", "mood_atmosphere", "composition_notes", 
        "camera_composition", "prompt_references", "relationships",
        "sexual_details", "sexual_content", "nsfw_elements", "nsfw_content",
        "technical_details", "technical", "art_style_tags", "art_styles",
        "lighting_quality", "lighting", "environment_details", "settings",
        "clothing_accessories", "clothing_items", "clothing",
        "pose_actions", "poses", "character_attributes", "character_eyes",
        "character_hair", "character_body_types", "character_ages",
        "character_genders", "characters"
    ]
    
    # Delete from related tables first (foreign key constraints)
    for table in tables:
        db.execute(f"DELETE FROM {table} WHERE prompt_id = ?", (prompt_id,))
    
    # Finally delete from prompts table
    db.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    
    db.commit()
    
    return None
