"""
Initialize User Preferences Table

Creates the user_preferences table in the users database.
"""

import sqlite3
from pathlib import Path


def init_preferences_table():
    """Create user_preferences table if it doesn't exist."""
    
    # Connect to users database (same location as init_users_db.py uses)
    db_path = Path(__file__).parent.parent / "data" / "users.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create user_preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                show_unspecified BOOLEAN DEFAULT 1,
                excluded_tags TEXT DEFAULT '["high quality", "masterpiece", "best quality"]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create trigger to update updated_at
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_preferences_timestamp 
            AFTER UPDATE ON user_preferences
            BEGIN
                UPDATE user_preferences 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE user_id = NEW.user_id;
            END
        """)
        
        conn.commit()
        print("✅ user_preferences table created successfully")
        
        # Show table info
        cursor.execute("PRAGMA table_info(user_preferences)")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("User Preferences Table Initialization")
    print("=" * 70)
    
    success = init_preferences_table()
    
    if success:
        print("\n✅ Initialization complete!")
    else:
        print("\n❌ Initialization failed!")
