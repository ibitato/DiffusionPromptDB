import os
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("JWT_SECRET_KEY", "testsecret")
os.environ.setdefault("API_KEYS", '["test_key"]')

from src.api.routers import prompts


def _make_db(existing_tags=None):
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE main_tags (prompt_id INTEGER, tag TEXT, tag_order INTEGER)"
    )
    existing_tags = existing_tags or []
    for idx, tag in enumerate(existing_tags, start=1):
        conn.execute(
            "INSERT INTO main_tags (prompt_id, tag, tag_order) VALUES (?, ?, ?)",
            (idx, tag, idx),
        )
    return conn


def test_infer_tags_falls_back_to_candidates_when_tag_missing():
    db = _make_db()
    tags = prompts._infer_tags_from_prompt("a photo of annitaxyz", db)  # noqa: SLF001
    assert tags == ["photo", "annitaxyz"]


def test_infer_tags_appends_new_tokens_after_existing_matches():
    db = _make_db(existing_tags=["photo"])
    tags = prompts._infer_tags_from_prompt("a photo of annitaxyz", db)  # noqa: SLF001
    assert tags == ["photo", "annitaxyz"]


def test_prepare_tags_accepts_new_catalog_entries(monkeypatch):
    monkeypatch.setattr(prompts.settings, "ingestion_default_tags", [])
    conn = sqlite3.connect(":memory:")
    result = prompts._prepare_tags(conn, "annitaxyz, photo")
    assert result == ["annitaxyz", "photo"]


def test_prepare_tags_deduplicates_and_applies_defaults(monkeypatch):
    monkeypatch.setattr(prompts.settings, "ingestion_default_tags", ["high quality"])
    conn = sqlite3.connect(":memory:")
    result = prompts._prepare_tags(conn, "photo, high quality")
    assert result == ["photo", "high quality"]
