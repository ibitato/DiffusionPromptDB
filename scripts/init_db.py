#!/usr/bin/env python3
"""
Script to initialize the DiffusionPromptDB database.
"""
import sys
from pathlib import Path

# Add parent directory to path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from diffusion_prompt_db.database import Database


def main():
    """Initialize the database."""
    print("Initializing DiffusionPromptDB...")
    print("-" * 50)
    
    db = Database()
    print(f"✓ Database created at: {db.db_path.absolute()}")
    print("✓ Tables and indexes created successfully")
    print("\nDatabase is ready to use!")
    db.close()


if __name__ == "__main__":
    main()
