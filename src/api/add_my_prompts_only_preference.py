#!/usr/bin/env python3
"""
Migration script to add my_prompts_only field to user_preferences table.

Adds:
- my_prompts_only (INTEGER DEFAULT 0) - Boolean stored as 0/1
"""

import sqlite3
from pathlib import Path
from config import settings


def migrate_database():
    """Add my_prompts_only column to user_preferences table."""
    # Use users.db path where preferences are actually stored
    db_path = Path(__file__).parent.parent / "data" / "users.db"

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False

    print(f"📊 Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user_preferences'"
        )
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            print(f"📋 Creating user_preferences table...")
            cursor.execute(
                """
                CREATE TABLE user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    show_unspecified INTEGER DEFAULT 1,
                    my_prompts_only INTEGER DEFAULT 0,
                    excluded_tags TEXT DEFAULT 'high quality,masterpiece,best quality'
                )
            """
            )
            print(f"   ✓ Table created successfully")
        else:
            print(f"✓ Table exists, checking columns...")
            # Check existing columns
            cursor.execute("PRAGMA table_info(user_preferences)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            print(f"✓ Existing columns: {existing_columns}")

            # Add my_prompts_only column if it doesn't exist
            if "my_prompts_only" not in existing_columns:
                print(f"➕ Adding column: my_prompts_only (INTEGER DEFAULT 0)")
                cursor.execute(
                    "ALTER TABLE user_preferences ADD COLUMN my_prompts_only INTEGER DEFAULT 0"
                )
                print(f"   ✓ Column my_prompts_only added successfully")
            else:
                print(f"⏭️  Column my_prompts_only already exists, skipping")

        conn.commit()

        # Verify changes
        cursor.execute("PRAGMA table_info(user_preferences)")
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
    print("  DATABASE MIGRATION: Add my_prompts_only Preference")
    print("=" * 60)
    print()

    success = migrate_database()

    if success:
        print("\n✅ You can now use my_prompts_only preference!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
