"""
Prompts Router

CRUD operations for original prompts.
"""

from datetime import datetime
import json
import re
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from typing import List, Optional, Dict, Any, Sequence
import sqlite3
from pathlib import Path

from ..models import PromptCreate, PromptUpdate, PromptResponse, PromptListResponse
from ..models.ingestion_models import BatchImageIngestionResponse, ImageIngestionResult
from ..auth import (
    verify_api_key,
    verify_token,
    verify_ownership_or_admin,
    optional_auth,
)
from ..config import settings
from ..services.image_metadata import (
    MetadataExtractionError,
    ExtractedMetadata,
    extract_png_metadata,
)
from ..services.image_storage import ImageStorageError, save_image_and_thumbnail

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
            p.image_path,
            p.thumbnail_path,
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
    row = _fetch_prompt_details(db, prompt_id)
    if not row:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return row


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

    next_id = _get_next_prompt_id(db)

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

    created = _fetch_prompt_details(db, next_id)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create prompt")
    return created


@router.post(
    "/ingest",
    response_model=BatchImageIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_prompts_from_images(
    files: List[UploadFile] = File(..., description="Stable Diffusion PNG files"),
    tags: Optional[str] = Form(
        None, description="Comma-separated tags that already exist in the catalog"
    ),
    category: Optional[str] = Form(
        None, description="Category to apply to every ingested prompt"
    ),
    art_style: Optional[str] = Form(
        None, description="Art style to store alongside the prompt"
    ),
    rating: Optional[int] = Form(
        None, description="Optional rating (1-5) applied to every prompt"
    ),
    notes: Optional[str] = Form(
        None, description="Additional notes stored with each prompt"
    ),
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token),
):
    """
    Allow any authenticated user to import SD PNGs into their own prompt catalog.
    """

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one PNG file must be provided.",
        )

    if rating is not None and (rating < 1 or rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5.",
        )

    user_id = auth.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authenticated user context required.")

    user_defined_tags = _prepare_tags(db, tags)
    results: List[ImageIngestionResult] = []
    created = 0

    for upload in files:
        filename = upload.filename or "unnamed.png"
        saved_paths: Optional[Sequence[Optional[str]]] = None

        try:
            data = await upload.read()
            if not data:
                raise MetadataExtractionError("Uploaded file is empty.")

            metadata = extract_png_metadata(data)
            prompt_text = metadata.positive_prompt or metadata.raw_parameters
            model_name = (
                metadata.settings.get("Model")
                or metadata.settings.get("model")
                or "unknown-model"
            )

            parameters_payload = json.dumps(
                {
                    "raw": metadata.raw_parameters,
                    "settings": metadata.settings,
                },
                ensure_ascii=False,
            )

            image_path, thumbnail_path = save_image_and_thumbnail(data, filename)
            saved_paths = (image_path, thumbnail_path)

            inferred_tags = _infer_tags_from_prompt(prompt_text, db)
            tags_for_prompt = _merge_tag_lists(user_defined_tags, inferred_tags)
            inferred_style = _infer_art_style(metadata)
            art_style_value = art_style or category or inferred_style

            prompt_id = _insert_ingested_prompt(
                db=db,
                text=prompt_text,
                negative_prompt=metadata.negative_prompt or None,
                model=model_name,
                parameters=parameters_payload,
                rating=rating,
                notes=notes,
                art_style=art_style_value,
                tags=tags_for_prompt,
                user_id=user_id,
                image_path=image_path,
                thumbnail_path=thumbnail_path,
            )
            db.commit()
            created += 1
            results.append(
                ImageIngestionResult(
                    filename=filename,
                    status="created",
                    detail="Prompt stored successfully.",
                    prompt_id=prompt_id,
                )
            )
        except MetadataExtractionError as exc:
            results.append(
                ImageIngestionResult(
                    filename=filename, status="failed", detail=str(exc), prompt_id=None
                )
            )
        except ImageStorageError as exc:
            _cleanup_files(saved_paths)
            results.append(
                ImageIngestionResult(
                    filename=filename, status="failed", detail=str(exc), prompt_id=None
                )
            )
        except sqlite3.Error as exc:
            db.rollback()
            _cleanup_files(saved_paths)
            results.append(
                ImageIngestionResult(
                    filename=filename,
                    status="failed",
                    detail="Database error while creating prompt.",
                    prompt_id=None,
                )
            )
        finally:
            await upload.close()

    failed = sum(1 for item in results if item.status != "created")
    return BatchImageIngestionResponse(created=created, failed=failed, results=results)


@router.post("/{prompt_id}/copy", response_model=PromptResponse, status_code=201)
async def copy_prompt(
    prompt_id: int,
    db: sqlite3.Connection = Depends(get_prompts_db),
    auth: dict = Depends(verify_token),
):
    """
    Create a personal copy of an existing catalog prompt.

    Requires: JWT Token
    """
    source = db.execute(
        """
        SELECT id, original_prompt, model_used, input_tokens, output_tokens,
               negative_prompt, parameters, rating, notes, image_path, thumbnail_path
        FROM prompts
        WHERE id = ?
    """,
        (prompt_id,),
    ).fetchone()

    if not source:
        raise HTTPException(status_code=404, detail="Prompt not found")

    next_id = _get_next_prompt_id(db)
    db.execute(
        """
        INSERT INTO prompts (
            id,
            original_prompt,
            processed_at,
            model_used,
            input_tokens,
            output_tokens,
            created_by,
            negative_prompt,
            parameters,
            rating,
            notes,
            image_path,
            thumbnail_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            next_id,
            source["original_prompt"],
            datetime.utcnow().isoformat(),
            source["model_used"],
            source["input_tokens"] or 0,
            source["output_tokens"] or 0,
            auth["user_id"],
            source["negative_prompt"],
            source["parameters"],
            source["rating"],
            source["notes"],
            source["image_path"],
            source["thumbnail_path"],
        ),
    )

    _clone_related_rows(db, prompt_id, next_id)
    db.commit()

    created = _fetch_prompt_details(db, next_id)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to copy prompt")
    return created


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
PROMPT_DETAILS_QUERY = """
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
            p.image_path,
            p.thumbnail_path,
            GROUP_CONCAT(DISTINCT t.tag) as tags,
            p.rating,
            p.notes
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        LEFT JOIN main_tags t ON p.id = t.prompt_id
        WHERE p.id = ?
        GROUP BY p.id
    """


def _fetch_prompt_details(db: sqlite3.Connection, prompt_id: int) -> Optional[Dict[str, Any]]:
    row = db.execute(PROMPT_DETAILS_QUERY, (prompt_id,)).fetchone()
    return dict(row) if row else None


def _get_next_prompt_id(db: sqlite3.Connection) -> int:
    max_id = db.execute("SELECT MAX(id) FROM prompts").fetchone()[0]
    return (max_id or 0) + 1


def _tables_with_prompt_id(db: sqlite3.Connection) -> List[List[str]]:
    tables = []
    for (name,) in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ):
        columns = [col[1] for col in db.execute(f"PRAGMA table_info('{name}')")]
        if "prompt_id" in columns and name != "prompts":
            tables.append((name, columns))
    return tables


def _clone_related_rows(db: sqlite3.Connection, source_id: int, target_id: int) -> None:
    for table, columns in _tables_with_prompt_id(db):
        rows = db.execute(
            f"SELECT {', '.join(columns)} FROM {table} WHERE prompt_id = ?",
            (source_id,),
        ).fetchall()
        if not rows:
            continue
        placeholders = ", ".join(["?"] * len(columns))
        prompt_idx = columns.index("prompt_id")
        for row in rows:
            values = list(row)
            values[prompt_idx] = target_id
            db.execute(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )


def _prepare_tags(db: sqlite3.Connection, tags_csv: Optional[str]) -> List[str]:
    """Normalize user-provided tags without enforcing catalog existence."""

    raw_tags: List[str] = []
    if tags_csv:
        raw_tags.extend([tag.strip() for tag in tags_csv.split(",") if tag.strip()])
    if settings.ingestion_default_tags:
        raw_tags.extend(
            [tag.strip() for tag in settings.ingestion_default_tags if tag.strip()]
        )

    ordered_unique: List[str] = []
    seen = set()
    for tag in raw_tags:
        if tag and tag not in seen:
            ordered_unique.append(tag)
            seen.add(tag)

    return ordered_unique


def _insert_ingested_prompt(
    *,
    db: sqlite3.Connection,
    text: str,
    negative_prompt: Optional[str],
    model: str,
    parameters: str,
    rating: Optional[int],
    notes: Optional[str],
    art_style: Optional[str],
    tags: List[str],
    user_id: int,
    image_path: Optional[str],
    thumbnail_path: str,
) -> int:
    """Persist a prompt and its related rows."""

    prompt_text = text.strip() or "Imported prompt"
    prompt_id = _get_next_prompt_id(db)
    processed_at = datetime.utcnow().isoformat()

    db.execute(
        """
        INSERT INTO prompts (
            id,
            original_prompt,
            processed_at,
            model_used,
            input_tokens,
            output_tokens,
            created_by,
            negative_prompt,
            parameters,
            rating,
            notes,
            image_path,
            thumbnail_path
        )
        VALUES (?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            prompt_id,
            prompt_text,
            processed_at,
            model,
            user_id,
            negative_prompt,
            parameters,
            rating,
            notes,
            image_path,
            thumbnail_path,
        ),
    )

    db.execute(
        "INSERT INTO characters (prompt_id, number_of_people, breast_size) VALUES (?, 1, 'unspecified')",
        (prompt_id,),
    )
    db.execute(
        "INSERT INTO nsfw_content (prompt_id, level) VALUES (?, 'safe')",
        (prompt_id,),
    )

    if art_style:
        db.execute(
            "INSERT INTO art_styles (prompt_id, primary_style) VALUES (?, ?)",
            (prompt_id, art_style),
        )

    for tag in tags:
        db.execute(
            "INSERT INTO main_tags (prompt_id, tag) VALUES (?, ?)",
            (prompt_id, tag),
        )

    return prompt_id


def _cleanup_files(paths: Optional[Sequence[Optional[str]]]) -> None:
    """Delete stored thumbnails when ingestion fails."""

    if not paths:
        return

    media_root = Path(settings.media_root).expanduser()
    for rel in paths:
        if not rel:
            continue
        try:
            target = media_root / rel
            if target.exists():
                target.unlink()
        except OSError:
            pass


TAG_SPLIT_RE = re.compile(r"[,\n]+")
TAG_SANITIZE_RE = re.compile(r"[()\[\]{}<>:\"'|*]")
STOPWORDS = {
    "and",
    "with",
    "the",
    "of",
    "in",
    "at",
    "by",
    "for",
    "to",
    "a",
    "an",
    "on",
}
ART_STYLE_KEYWORDS = [
    ("anime", "Anime"),
    ("manga", "Anime"),
    ("comic", "Comic Book"),
    ("mangastyle", "Anime"),
    ("watercolor", "Watercolor"),
    ("oil painting", "Oil Painting"),
    ("digital painting", "Digital Painting"),
    ("painterly", "Digital Painting"),
    ("cinematic", "Cinematic"),
    ("film still", "Cinematic"),
    ("photograph", "Photorealistic"),
    ("photo", "Photorealistic"),
    ("realistic", "Realistic"),
    ("hyperrealistic", "Photorealistic"),
    ("fantasy", "Fantasy Art"),
    ("cyberpunk", "Cyberpunk"),
    ("pixel", "Pixel Art"),
    ("low poly", "Low Poly"),
    ("3d render", "3D Render"),
    ("render", "3D Render"),
]


MAX_INFERRED_TAGS = 25


def _infer_tags_from_prompt(prompt_text: str, db: sqlite3.Connection) -> List[str]:
    candidates = _extract_candidate_tags(prompt_text or "")
    if not candidates:
        return []

    matched = _match_existing_tags(db, candidates)
    if not matched:
        # Nothing in catalog yet: keep original candidates so new tags surface.
        return candidates[:MAX_INFERRED_TAGS]

    matched_set = set(matched)
    extended = matched + [tag for tag in candidates if tag not in matched_set]
    return extended[:MAX_INFERRED_TAGS]


def _extract_candidate_tags(prompt_text: str) -> List[str]:
    if not prompt_text:
        return []
    candidates: List[str] = []
    seen = set()
    for chunk in TAG_SPLIT_RE.split(prompt_text):
        cleaned = TAG_SANITIZE_RE.sub("", chunk).strip().lower()
        if not cleaned:
            continue
        for raw_token in cleaned.split():
            token = raw_token.strip().strip("-_")
            if not token or token in STOPWORDS or len(token) < 2:
                continue
            if token not in seen:
                seen.add(token)
                candidates.append(token)
    return candidates[:60]


def _match_existing_tags(db: sqlite3.Connection, candidates: List[str]) -> List[str]:
    if not candidates:
        return []
    placeholders = ", ".join("?" * len(candidates))
    rows = db.execute(
        f"SELECT DISTINCT tag FROM main_tags WHERE tag IN ({placeholders})",
        candidates,
    ).fetchall()
    existing = {row[0] for row in rows}
    return [tag for tag in candidates if tag in existing]


def _merge_tag_lists(primary: List[str], secondary: List[str]) -> List[str]:
    merged: List[str] = []
    seen = set()
    for source in (primary, secondary):
        for tag in source:
            if tag and tag not in seen:
                seen.add(tag)
                merged.append(tag)
    return merged


def _infer_art_style(metadata: ExtractedMetadata) -> Optional[str]:
    corpus = " ".join(
        [
            (metadata.positive_prompt or "").lower(),
            (metadata.raw_parameters or "").lower(),
            (metadata.settings.get("Model") or metadata.settings.get("model") or "").lower(),
        ]
    )
    for keyword, style in ART_STYLE_KEYWORDS:
        if keyword in corpus:
            return style
    return None
