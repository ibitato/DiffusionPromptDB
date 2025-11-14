#!/usr/bin/env python3
"""
Migration script to add missing fields to prompts table.

Adds:
- negative_prompt (TEXT)
- parameters (TEXT)
- rating (INTEGER)
- notes (TEXT)
"""

import sqlite3
from pathlib import Path
from config import settings


def migrate_database():
    """Add missing columns to prompts table."""
    db_path = Path(settings.prompts_db_path)

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False

    print(f"📊 Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(prompts)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"✓ Existing columns: {existing_columns}")

        # Add missing columns
        columns_to_add = {
            "negative_prompt": "TEXT",
            "parameters": "TEXT",
            "rating": "INTEGER",
            "notes": "TEXT",
        }

        for column_name, column_type in columns_to_add.items():
            if column_name not in existing_columns:
                print(f"➕ Adding column: {column_name} ({column_type})")
                cursor.execute(
                    f"ALTER TABLE prompts ADD COLUMN {column_name} {column_type}"
                )
                print(f"   ✓ Column {column_name} added successfully")
            else:
                print(f"⏭️  Column {column_name} already exists, skipping")

        conn.commit()

        # Verify changes
        cursor.execute("PRAGMA table_info(prompts)")
        new_columns = {row[1] for row in cursor.fetchall()}
        print(f"\n✅ Final columns: {new_columns}")

        print("\n🎉 Migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  DATABASE MIGRATION: Add Missing Prompt Fields")
    print("=" * 60)
    print()

    success = migrate_database()

    if success:
        print(
            "\n✅ You can now use negative_prompt, parameters, rating, and notes fields!"
        )
    else:
        print("\n❌ Migration failed. Please check the errors above.")
