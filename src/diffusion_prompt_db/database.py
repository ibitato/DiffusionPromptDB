"""
Database management for DiffusionPromptDB using SQLite.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from .models import Prompt


class Database:
    """SQLite database manager for diffusion prompts."""

    def __init__(self, db_path: str = "data/prompts.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.connect()
        self._create_tables()

    def connect(self):
        """Establish connection to database."""
        self.connection = sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.connection.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                negative_prompt TEXT,
                model TEXT,
                parameters TEXT,
                tags TEXT,
                category TEXT,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes for common queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_prompts_category
            ON prompts(category)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_prompts_model
            ON prompts(model)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_prompts_rating
            ON prompts(rating)
        """
        )

        self.connection.commit()

    def add_prompt(self, prompt: Prompt) -> int:
        """
        Add a new prompt to database.

        Args:
            prompt: Prompt object to add

        Returns:
            ID of inserted prompt
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO prompts
            (text, negative_prompt, model, parameters, tags, category, rating, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                prompt.text,
                prompt.negative_prompt,
                prompt.model,
                prompt.parameters,
                prompt.tags,
                prompt.category,
                prompt.rating,
                prompt.notes,
            ),
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_prompt(self, prompt_id: int) -> Optional[Prompt]:
        """
        Get a prompt by ID.

        Args:
            prompt_id: ID of prompt to retrieve

        Returns:
            Prompt object or None if not found
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()

        if row:
            return self._row_to_prompt(row)
        return None

    def get_all_prompts(self, limit: Optional[int] = None) -> List[Prompt]:
        """
        Get all prompts from database.

        Args:
            limit: Maximum number of prompts to return

        Returns:
            List of Prompt objects
        """
        cursor = self.connection.cursor()
        query = "SELECT * FROM prompts ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        return [self._row_to_prompt(row) for row in cursor.fetchall()]

    def search_prompts(
        self,
        text: Optional[str] = None,
        category: Optional[str] = None,
        model: Optional[str] = None,
        min_rating: Optional[int] = None,
    ) -> List[Prompt]:
        """
        Search prompts with filters.

        Args:
            text: Search in prompt text
            category: Filter by category
            model: Filter by model
            min_rating: Filter by minimum rating

        Returns:
            List of matching Prompt objects
        """
        cursor = self.connection.cursor()
        conditions = []
        params = []

        if text:
            conditions.append("text LIKE ?")
            params.append(f"%{text}%")

        if category:
            conditions.append("category = ?")
            params.append(category)

        if model:
            conditions.append("model = ?")
            params.append(model)

        if min_rating:
            conditions.append("rating >= ?")
            params.append(min_rating)

        query = "SELECT * FROM prompts"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        return [self._row_to_prompt(row) for row in cursor.fetchall()]

    def update_prompt(self, prompt_id: int, prompt: Prompt) -> bool:
        """
        Update an existing prompt.

        Args:
            prompt_id: ID of prompt to update
            prompt: Prompt object with updated data

        Returns:
            True if updated, False if not found
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE prompts
            SET text = ?, negative_prompt = ?, model = ?, parameters = ?,
                tags = ?, category = ?, rating = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            (
                prompt.text,
                prompt.negative_prompt,
                prompt.model,
                prompt.parameters,
                prompt.tags,
                prompt.category,
                prompt.rating,
                prompt.notes,
                prompt_id,
            ),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_prompt(self, prompt_id: int) -> bool:
        """
        Delete a prompt.

        Args:
            prompt_id: ID of prompt to delete

        Returns:
            True if deleted, False if not found
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def _row_to_prompt(self, row: sqlite3.Row) -> Prompt:
        """Convert database row to Prompt object."""
        # Handle timestamp conversion - SQLite may return datetime objects or strings
        created_at = row["created_at"]
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = row["updated_at"]
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return Prompt(
            id=row["id"],
            text=row["text"],
            negative_prompt=row["negative_prompt"],
            model=row["model"],
            parameters=row["parameters"],
            tags=row["tags"],
            category=row["category"],
            rating=row["rating"],
            notes=row["notes"],
            created_at=created_at,
            updated_at=updated_at,
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
