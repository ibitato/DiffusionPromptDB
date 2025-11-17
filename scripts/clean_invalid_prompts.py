#!/usr/bin/env python3
"""
Utility to remove invalid prompts from the catalog database.

The initial Stable Diffusion dump contains narrative messages (e.g. “If you would
like the prompt codes and Loras...”) that are not real prompts. This script
identifies prompts whose text contains suspicious phrases and deletes them along
with any related rows (tags, art styles, NSFW metadata, etc.).
"""

from __future__ import annotations

import argparse
import sqlite3
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable, List, Sequence

DEFAULT_PATTERNS = [
    "prompt codes and loras",
    "view button on the top left",
    "buzz everyone",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        default="database/prompts_catalog.db",
        help="Path to prompts catalog SQLite database",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        help="Additional substring (case-insensitive) to match in original_prompt. "
        "May be passed multiple times.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persist deletions. Without this flag the script only reports matches.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip automatic backup before deleting.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=200,
        help="Batch size for DELETE statements (default: 200)",
    )
    return parser.parse_args()


def ensure_backup(db_path: Path) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{db_path.stem}-{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return backup_path


def chunked(seq: Sequence[int], size: int) -> Iterable[Sequence[int]]:
    for idx in range(0, len(seq), size):
        yield seq[idx : idx + size]


def resolve_tables(conn: sqlite3.Connection) -> List[str]:
    tables = []
    for (name,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ):
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info('{name}')")}
        if "prompt_id" in columns and name != "prompts":
            tables.append(name)
    return tables


def main() -> None:
    args = parse_args()
    db_path = Path(args.db).resolve()
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    patterns = args.patterns or DEFAULT_PATTERNS
    lowered_patterns = [p.lower() for p in patterns]

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")

    placeholders = " OR ".join("LOWER(original_prompt) LIKE ?" for _ in lowered_patterns)
    params = [f"%{pat}%" for pat in lowered_patterns]
    rows = conn.execute(
        f"SELECT id, original_prompt FROM prompts WHERE {placeholders}", params
    ).fetchall()

    if not rows:
        print("No prompts matched the provided patterns.")
        return

    matched_ids = [row[0] for row in rows]
    print(f"Matched {len(matched_ids)} prompts.")
    preview = "\n".join(f"- #{row[0]}: {row[1][:80]}..." for row in rows[:5])
    if preview:
        print("Sample:")
        print(preview)

    if not args.apply:
        print("\nRun again with --apply to delete these records.")
        return

    if not args.no_backup:
        backup_path = ensure_backup(db_path)
        print(f"Backup created at {backup_path}")

    child_tables = resolve_tables(conn)
    print(f"Deleting from {len(child_tables)} related tables.")

    for chunk in chunked(matched_ids, args.chunk_size):
        placeholders = ",".join("?" * len(chunk))
        for table in child_tables:
            conn.execute(f"DELETE FROM {table} WHERE prompt_id IN ({placeholders})", chunk)
        conn.execute(f"DELETE FROM prompts WHERE id IN ({placeholders})", chunk)

    conn.commit()
    print(f"Deleted {len(matched_ids)} prompts and their related metadata.")


if __name__ == "__main__":
    main()
