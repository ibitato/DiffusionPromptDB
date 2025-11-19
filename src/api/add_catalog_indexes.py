#!/usr/bin/env python3
"""
Ensure critical indexes exist in the catalog database to speed up queries.
"""

import sqlite3
from pathlib import Path

from config import settings

INDEX_DEFINITIONS = [
    ("idx_prompts_processed_at", "prompts", "processed_at"),
    ("idx_prompts_created_by", "prompts", "created_by"),
    ("idx_prompts_model_used", "prompts", "model_used"),
    # Composite index accelerates "my prompts" queries that filter by user and
    # order by recency (processed_at DESC) without forcing a temp sort.
    (
        "idx_prompts_created_by_processed_at",
        "prompts",
        "created_by, processed_at DESC",
    ),
    ("idx_nsfw_content_prompt_id", "nsfw_content", "prompt_id"),
    ("idx_art_styles_prompt_id", "art_styles", "prompt_id"),
    ("idx_main_tags_prompt_id", "main_tags", "prompt_id"),
    ("idx_characters_prompt_id", "characters", "prompt_id"),
]


def ensure_indexes() -> None:
    db_path = Path(settings.catalog_db_path).expanduser()
    if not db_path.exists():
        raise SystemExit(f"Catalog DB not found at {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for index_name, table, column in INDEX_DEFINITIONS:
        cursor.execute(
            f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})"
        )

    conn.commit()
    conn.close()
    print(f"✅ Indexes ensured on {db_path}")


if __name__ == "__main__":
    ensure_indexes()
