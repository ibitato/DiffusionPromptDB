"""
Prompts Router

CRUD operations for original prompts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
import sqlite3
from pathlib import Path

from ..models import PromptCreate, PromptUpdate, PromptResponse, PromptListResponse
from ..auth import (
    verify_api_key,
    verify_token,
    verify_admin,
    verify_ownership_or_admin,
    optional_auth,
)
from ..config import settings
from typing import Optional

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
    my_prompts: Optional[bool] = Query(
        None, description="Filter to only show user's own prompts"
    ),
    db: sqlite3.Connection = Depends(get_prompts_db),
    api_key: str = Depends(verify_api_key),
    auth_info: Optional[dict] = Depends(optional_auth),
):
    """
    List prompts with pagination.
    Uses catalog DB schema (original_prompt, processed_at).

    Requires: API Key
    """
    offset = (page - 1) * page_size

    # Build WHERE clause for my_prompts filter
    where_clause = ""
    count_params = []

    print(f"DEBUG PROMPTS: my_prompts={my_prompts}, auth_info={auth_info}")  # Debug

    if my_prompts and auth_info:
        user_id = auth_info.get("user_id")
        if user_id:
            where_clause = "WHERE p.created_by = ?"
            count_params = [user_id]
            print(f"DEBUG PROMPTS: ✅ Filtering by user_id={user_id}")  # Debug
        else:
            print(f"DEBUG PROMPTS: ⚠️  auth_info exists but no user_id: {auth_info}")
    elif my_prompts:
        print(f"DEBUG PROMPTS: ⚠️  my_prompts=true but auth_info is None")

    # Count total with filter
    count_query = f"SELECT COUNT(*) FROM prompts p {where_clause}"
    total = db.execute(count_query, count_params).fetchone()[0]

    # Get results - map catalog fields to expected frontend fields
    query = f"""
        SELECT 
            p.id,
            p.original_prompt as text,
            p.model_used as model,
            p.processed_at as created_at,
            p.processed_at as updated_at,
            p.created_by,
            a.primary_style as category,
            a.primary_style as art_style,
            p.negative_prompt,
            p.parameters,
            GROUP_CONCAT(DISTINCT t.tag) as tags,
            p.rating,
            p.notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        LEFT JOIN main_tags t ON p.id = t.prompt_id
        {where_clause}
        GROUP BY p.id
        ORDER BY p.processed_at DESC
        LIMIT ? OFFSET ?
    """
    params = count_params + [page_size, offset]

    # Get results
    results = db.execute(query, params).fetchall()

    prompts = [dict(row) for row in results]
    print(
        f"DEBUG PROMPTS: response count={len(prompts)} total={total} using filter={where_clause!r}"
    )

    return {"total": total, "page": page, "page_size": page_size, "results": prompts}


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: int,
    db: sqlite3.Connection = Depends(get_prompts_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Get a specific prompt by ID.
    Maps catalog schema to frontend expected schema.

    Requires: API Key
    """
    # Get prompt with mapped fields including tags and art_style
    row = db.execute(
        """
        SELECT 
            p.id,
            p.original_prompt as text,
            p.model_used as model,
            p.processed_at as created_at,
            p.processed_at as updated_at,
            p.created_by,
            a.primary_style as category,
            a.primary_style as art_style,
            p.negative_prompt,
            p.parameters,
            GROUP_CONCAT(DISTINCT t.tag) as tags,
            p.rating,
            p.notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        LEFT JOIN main_tags t ON p.id = t.prompt_id
        WHERE p.id = ?
        GROUP BY p.id
    """,
        (prompt_id,),
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return dict(row)


@router.post("/", response_model=PromptResponse, status_code=201)
async def create_prompt(
    prompt: PromptCreate,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token),
):
    """
    Create a new prompt in catalog DB.
    Any authenticated user can create their own prompts.

    Requires: JWT Token
    """
    user_id = auth["user_id"]
    from datetime import datetime

    # Get next ID
    max_id = db.execute("SELECT MAX(id) FROM prompts").fetchone()[0]
    next_id = (max_id or 0) + 1

    # Insert into prompts table (catalog schema) with created_by and new fields
    db.execute(
        """
        INSERT INTO prompts (id, original_prompt, processed_at, model_used, input_tokens, output_tokens, created_by, 
                           negative_prompt, parameters, rating, notes)
        VALUES (?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?)
    """,
        (
            next_id,
            prompt.text,
            datetime.utcnow().isoformat(),
            prompt.model or "manual-entry",
            user_id,
            prompt.negative_prompt,
            prompt.parameters,
            prompt.rating,
            prompt.notes,
        ),
    )

    # Insert basic categorization
    db.execute(
        "INSERT INTO characters (prompt_id, number_of_people, breast_size) VALUES (?, 1, 'unspecified')",
        (next_id,),
    )
    db.execute(
        "INSERT INTO nsfw_content (prompt_id, level) VALUES (?, 'safe')", (next_id,)
    )

    # Handle art_style (using category field for backward compatibility)
    art_style_value = prompt.art_style or prompt.category
    if art_style_value:
        db.execute(
            "INSERT INTO art_styles (prompt_id, primary_style) VALUES (?, ?)",
            (next_id, art_style_value),
        )

    # Handle tags
    if prompt.tags:
        tags_list = [tag.strip() for tag in prompt.tags.split(",") if tag.strip()]
        for tag in tags_list:
            db.execute(
                "INSERT INTO main_tags (prompt_id, tag) VALUES (?, ?)",
                (next_id, tag),
            )

    db.commit()

    # Return created prompt with mapping including tags and art_style
    row = db.execute(
        """
        SELECT 
            p.id,
            p.original_prompt as text,
            p.model_used as model,
            p.processed_at as created_at,
            p.processed_at as updated_at,
            p.created_by,
            a.primary_style as category,
            a.primary_style as art_style,
            p.negative_prompt,
            p.parameters,
            GROUP_CONCAT(DISTINCT t.tag) as tags,
            p.rating,
            p.notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        LEFT JOIN main_tags t ON p.id = t.prompt_id
        WHERE p.id = ?
        GROUP BY p.id
    """,
        (next_id,),
    ).fetchone()

    return dict(row)


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt: PromptUpdate,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token),
):
    """
    Update an existing prompt in catalog DB.
    Updates prompt text and category (art_style).
    User can only update their own prompts, admin can update all.

    Requires: JWT Token (owner or admin)
    """
    # Verify ownership or admin
    verify_ownership_or_admin(prompt_id, auth, db)

    # Update prompt text
    if prompt.text is not None:
        db.execute(
            "UPDATE prompts SET original_prompt = ? WHERE id = ?",
            (prompt.text, prompt_id),
        )

    # Update model
    if prompt.model is not None:
        db.execute(
            "UPDATE prompts SET model_used = ? WHERE id = ?", (prompt.model, prompt_id)
        )

    # Update new fields
    if prompt.negative_prompt is not None:
        db.execute(
            "UPDATE prompts SET negative_prompt = ? WHERE id = ?",
            (prompt.negative_prompt, prompt_id),
        )

    if prompt.parameters is not None:
        db.execute(
            "UPDATE prompts SET parameters = ? WHERE id = ?",
            (prompt.parameters, prompt_id),
        )

    if prompt.rating is not None:
        db.execute(
            "UPDATE prompts SET rating = ? WHERE id = ?",
            (prompt.rating, prompt_id),
        )

    if prompt.notes is not None:
        db.execute(
            "UPDATE prompts SET notes = ? WHERE id = ?",
            (prompt.notes, prompt_id),
        )

    # Update art_style (using art_style field primarily, fallback to category)
    if prompt.art_style is not None or prompt.category is not None:
        art_style_value = (
            prompt.art_style if prompt.art_style is not None else prompt.category
        )
        # Check if art_style entry exists
        exists = db.execute(
            "SELECT 1 FROM art_styles WHERE prompt_id = ?", (prompt_id,)
        ).fetchone()
        if exists:
            db.execute(
                "UPDATE art_styles SET primary_style = ? WHERE prompt_id = ?",
                (art_style_value, prompt_id),
            )
        else:
            db.execute(
                "INSERT INTO art_styles (prompt_id, primary_style) VALUES (?, ?)",
                (prompt_id, art_style_value),
            )

    # Update tags
    if prompt.tags is not None:
        # Delete existing tags
        db.execute("DELETE FROM main_tags WHERE prompt_id = ?", (prompt_id,))

        # Insert new tags
        if prompt.tags:
            tags_list = [tag.strip() for tag in prompt.tags.split(",") if tag.strip()]
            for tag in tags_list:
                db.execute(
                    "INSERT INTO main_tags (prompt_id, tag) VALUES (?, ?)",
                    (prompt_id, tag),
                )

    db.commit()

    # Return updated prompt with mapping including tags and art_style
    row = db.execute(
        """
        SELECT 
            p.id,
            p.original_prompt as text,
            p.model_used as model,
            p.processed_at as created_at,
            p.processed_at as updated_at,
            p.created_by,
            a.primary_style as category,
            a.primary_style as art_style,
            p.negative_prompt,
            p.parameters,
            GROUP_CONCAT(DISTINCT t.tag) as tags,
            p.rating,
            p.notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        LEFT JOIN main_tags t ON p.id = t.prompt_id
        WHERE p.id = ?
        GROUP BY p.id
    """,
        (prompt_id,),
    ).fetchone()

    return dict(row)


# Whitelist of allowed tables for cascade delete (SQL injection protection)
ALLOWED_TABLES = frozenset(
    [
        "main_tags",
        "emotions",
        "mood_atmosphere",
        "composition_notes",
        "camera_composition",
        "prompt_references",
        "relationships",
        "sexual_details",
        "sexual_content",
        "nsfw_elements",
        "nsfw_content",
        "technical_details",
        "technical",
        "art_style_tags",
        "art_styles",
        "lighting_quality",
        "lighting",
        "environment_details",
        "settings",
        "clothing_accessories",
        "clothing_items",
        "clothing",
        "pose_actions",
        "poses",
        "character_attributes",
        "character_eyes",
        "character_hair",
        "character_body_types",
        "character_ages",
        "character_genders",
        "characters",
    ]
)


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(
    prompt_id: int,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token),
):
    """
    Delete a prompt from catalog DB.
    Cascades to all related tables using whitelist for SQL injection protection.
    User can only delete their own prompts, admin can delete all.

    Requires: JWT Token (owner or admin)
    """
    # Verify ownership or admin
    verify_ownership_or_admin(prompt_id, auth, db)

    # Delete from related tables first (foreign key constraints)
    # Using whitelist to prevent SQL injection via table name manipulation
    for table in ALLOWED_TABLES:
        db.execute(f"DELETE FROM {table} WHERE prompt_id = ?", (prompt_id,))

    # Finally delete from prompts table
    db.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))

    db.commit()

    return None
