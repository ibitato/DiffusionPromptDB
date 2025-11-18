#!/usr/bin/env python3
"""
Migration script to add image metadata columns to the prompts table.

Adds:
- image_path (TEXT)
- thumbnail_path (TEXT)
"""

import sqlite3
from pathlib import Path
from config import settings


def migrate_database() -> bool:
    """Ensure the prompts table has the columns required for media storage."""

    db_path = Path(settings.prompts_db_path)
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False

    print(f"📦 Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(prompts)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"   ✓ Existing columns: {existing_columns}")

        columns_to_add = {
            "image_path": "TEXT",
            "thumbnail_path": "TEXT",
        }

        for column_name, column_type in columns_to_add.items():
            if column_name not in existing_columns:
                print(f"➕ Adding column {column_name} ({column_type})")
                cursor.execute(
                    f"ALTER TABLE prompts ADD COLUMN {column_name} {column_type}"
                )
                print(f"   ✓ Column {column_name} added")
            else:
                print(f"⏭️  Column {column_name} already exists, skipping")

        conn.commit()

        cursor.execute("PRAGMA table_info(prompts)")
        final_columns = {row[1] for row in cursor.fetchall()}
        print(f"🎯 Final columns: {final_columns}")
        print("✅ Migration completed successfully")
        return True

    except sqlite3.Error as exc:
        print(f"❌ Migration failed: {exc}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    success = migrate_database()
    if not success:
        raise SystemExit(1)
