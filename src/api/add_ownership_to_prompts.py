"""
Add Ownership to Prompts Table

Adds created_by column to track prompt ownership.
"""

import sqlite3
from pathlib import Path


def add_ownership_column():
    """Add created_by column to prompts table."""

    # Connect to prompts database
    db_path = Path(__file__).parent / "database" / "prompts_catalog.db"

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(prompts)")
        columns = [col[1] for col in cursor.fetchall()]

        if "created_by" in columns:
            print("✅ Column 'created_by' already exists")
            return True

        # Add created_by column (NULL = precargado, user_id = creado por usuario)
        cursor.execute(
            """
            ALTER TABLE prompts 
            ADD COLUMN created_by INTEGER DEFAULT NULL
        """
        )

        conn.commit()
        print("✅ Column 'created_by' added successfully")
        print("   - NULL = Precargado (solo admin puede modificar)")
        print("   - user_id = Creado por usuario (usuario o admin pueden modificar)")

        # Show updated structure
        cursor.execute("PRAGMA table_info(prompts)")
        columns = cursor.fetchall()
        print("\nUpdated table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        return True

    except Exception as e:
        print(f"❌ Error adding column: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("Add Ownership to Prompts Table")
    print("=" * 70)

    success = add_ownership_column()

    if success:
        print("\n✅ Migration complete!")
        print("All existing prompts are marked as precargados (created_by = NULL)")
    else:
        print("\n❌ Migration failed!")
