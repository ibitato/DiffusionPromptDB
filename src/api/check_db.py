import sqlite3
from pathlib import Path

# Use the same path as in config.py
db_path = Path('src/api/database/prompts_catalog.db')

if not db_path.exists():
    print(f"Database not found at: {db_path}")
else:
    print(f"Database found at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check prompts table
    cursor.execute('SELECT COUNT(*) FROM prompts')
    print(f'Total prompts: {cursor.fetchone()[0]}')
    
    # Check for tags and art_styles
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"\nAvailable tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check sample prompt with tags and art_style
    cursor.execute("""
        SELECT 
            p.id,
            p.original_prompt,
            p.created_by,
            a.primary_style as art_style,
            GROUP_CONCAT(DISTINCT t.tag) as tags
        FROM prompts p
        LEFT JOIN art_styles a ON p.id = a.prompt_id
        LEFT JOIN main_tags t ON p.id = t.prompt_id
        WHERE p.id > 10000
        GROUP BY p.id
        LIMIT 5
    """)
    
    print(f"\nSample prompts with tags and art_styles:")
    for row in cursor.fetchall():
        print(f"ID {row['id']}: {row['original_prompt'][:50]}...")
        print(f"  Created by: {row['created_by']}")
        print(f"  Art style: {row['art_style']}")
        print(f"  Tags: {row['tags']}")
        print()
    
    conn.close()
