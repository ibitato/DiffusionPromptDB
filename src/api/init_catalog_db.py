#!/usr/bin/env python3
"""
Initialize the catalog database with proper schema
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def init_catalog_db():
    """Initialize catalog database with all required tables."""

    # Database path
    db_path = Path("catalog.db")

    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create all tables
    tables = [
        """
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY,
            original_prompt TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            model_used TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            created_by INTEGER DEFAULT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS characters (
            prompt_id INTEGER PRIMARY KEY,
            number_of_people INTEGER,
            breast_size TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS nsfw_content (
            prompt_id INTEGER PRIMARY KEY,
            level TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS art_styles (
            prompt_id INTEGER PRIMARY KEY,
            primary_style TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS main_tags (
            prompt_id INTEGER,
            tag TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS art_style_tags (
            prompt_id INTEGER,
            tag TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS emotions (
            prompt_id INTEGER,
            emotion TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS mood_atmosphere (
            prompt_id INTEGER,
            mood TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS composition_notes (
            prompt_id INTEGER,
            note TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS camera_composition (
            prompt_id INTEGER,
            composition TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS prompt_references (
            prompt_id INTEGER,
            reference TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS relationships (
            prompt_id INTEGER,
            relationship TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sexual_details (
            prompt_id INTEGER,
            detail TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sexual_content (
            prompt_id INTEGER,
            content TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS nsfw_elements (
            prompt_id INTEGER,
            element TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS technical_details (
            prompt_id INTEGER,
            detail TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS technical (
            prompt_id INTEGER,
            technical TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS lighting_quality (
            prompt_id INTEGER,
            quality TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS lighting (
            prompt_id INTEGER,
            lighting TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS environment_details (
            prompt_id INTEGER,
            detail TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS settings (
            prompt_id INTEGER,
            setting TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS clothing_accessories (
            prompt_id INTEGER,
            accessory TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS clothing_items (
            prompt_id INTEGER,
            item TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS clothing (
            prompt_id INTEGER,
            clothing TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS pose_actions (
            prompt_id INTEGER,
            action TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS poses (
            prompt_id INTEGER,
            pose TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS character_attributes (
            prompt_id INTEGER,
            attribute TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS character_eyes (
            prompt_id INTEGER,
            eye_detail TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS character_hair (
            prompt_id INTEGER,
            hair_detail TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS character_body_types (
            prompt_id INTEGER,
            body_type TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS character_ages (
            prompt_id INTEGER,
            age TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS character_genders (
            prompt_id INTEGER,
            gender TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
        """,
    ]

    # Create all tables
    for table_sql in tables:
        cursor.execute(table_sql)

    # Insert sample data
    sample_prompts = [
        {
            "id": 1,
            "text": "A beautiful landscape with mountains and a lake at sunset, digital art, highly detailed",
            "model": "stable-diffusion-v1.5",
            "art_style": "digital art",
            "tags": ["landscape", "mountains", "lake", "sunset", "detailed"],
            "nsfw_level": "safe",
        },
        {
            "id": 2,
            "text": "Anime style character portrait, blue hair, school uniform, cherry blossoms background",
            "model": "anything-v4.0",
            "art_style": "anime",
            "tags": ["anime", "portrait", "character", "school", "cherry blossoms"],
            "nsfw_level": "safe",
        },
        {
            "id": 3,
            "text": "Cyberpunk city at night, neon lights, rain, realistic photography style",
            "model": "stable-diffusion-xl",
            "art_style": "realistic",
            "tags": ["cyberpunk", "city", "night", "neon", "rain", "photography"],
            "nsfw_level": "safe",
        },
    ]

    for prompt in sample_prompts:
        # Insert prompt
        cursor.execute(
            """INSERT INTO prompts (id, original_prompt, processed_at, model_used, created_by) 
               VALUES (?, ?, ?, ?, NULL)""",
            (
                prompt["id"],
                prompt["text"],
                datetime.utcnow().isoformat(),
                prompt["model"],
            ),
        )

        # Insert character data
        cursor.execute(
            "INSERT INTO characters (prompt_id, number_of_people, breast_size) VALUES (?, 1, 'unspecified')",
            (prompt["id"],),
        )

        # Insert NSFW level
        cursor.execute(
            "INSERT INTO nsfw_content (prompt_id, level) VALUES (?, ?)",
            (prompt["id"], prompt["nsfw_level"]),
        )

        # Insert art style
        cursor.execute(
            "INSERT INTO art_styles (prompt_id, primary_style) VALUES (?, ?)",
            (prompt["id"], prompt["art_style"]),
        )

        # Insert tags
        for tag in prompt["tags"]:
            cursor.execute(
                "INSERT INTO main_tags (prompt_id, tag) VALUES (?, ?)",
                (prompt["id"], tag),
            )

    # Commit changes
    conn.commit()
    conn.close()

    print(f"Database initialized at: {db_path.absolute()}")
    print(f"Created {len(tables)} tables")
    print(f"Inserted {len(sample_prompts)} sample prompts")


if __name__ == "__main__":
    init_catalog_db()
