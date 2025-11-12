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
    conn = sqlite3.connect(db_path)
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
    
    Requires: API Key
    """
    offset = (page - 1) * page_size
    
    # Count total
    if category:
        total = db.execute("SELECT COUNT(*) FROM prompts WHERE category = ?", (category,)).fetchone()[0]
        query = "SELECT * FROM prompts WHERE category = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params = (category, page_size, offset)
    else:
        total = db.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
        query = "SELECT * FROM prompts ORDER BY created_at DESC LIMIT ? OFFSET ?"
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
    
    Requires: API Key
    """
    row = db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    
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
    Create a new prompt.
    
    Requires: JWT Token (write access)
    """
    cursor = db.execute("""
        INSERT INTO prompts (text, negative_prompt, model, parameters, tags, category, rating, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prompt.text,
        prompt.negative_prompt,
        prompt.model,
        prompt.parameters,
        prompt.tags,
        prompt.category,
        prompt.rating,
        prompt.notes
    ))
    
    db.commit()
    prompt_id = cursor.lastrowid
    
    # Return created prompt
    row = db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    return dict(row)


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt: PromptUpdate,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token)
):
    """
    Update an existing prompt.
    
    Requires: JWT Token (write access)
    """
    # Check if exists
    existing = db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Build update query dynamically
    updates = []
    values = []
    
    if prompt.text is not None:
        updates.append("text = ?")
        values.append(prompt.text)
    if prompt.negative_prompt is not None:
        updates.append("negative_prompt = ?")
        values.append(prompt.negative_prompt)
    if prompt.model is not None:
        updates.append("model = ?")
        values.append(prompt.model)
    if prompt.parameters is not None:
        updates.append("parameters = ?")
        values.append(prompt.parameters)
    if prompt.tags is not None:
        updates.append("tags = ?")
        values.append(prompt.tags)
    if prompt.category is not None:
        updates.append("category = ?")
        values.append(prompt.category)
    if prompt.rating is not None:
        updates.append("rating = ?")
        values.append(prompt.rating)
    if prompt.notes is not None:
        updates.append("notes = ?")
        values.append(prompt.notes)
    
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(prompt_id)
        
        query = f"UPDATE prompts SET {', '.join(updates)} WHERE id = ?"
        db.execute(query, values)
        db.commit()
    
    # Return updated prompt
    row = db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    return dict(row)


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(
    prompt_id: int,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token)
):
    """
    Delete a prompt.
    
    Requires: JWT Token (write access)
    """
    result = db.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return None
