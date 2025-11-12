"""
Configuration management for DiffusionPromptDB.
"""
from pathlib import Path


# Default configuration
DEFAULT_DB_PATH = "data/prompts.db"
DEFAULT_DATA_DIR = Path("data")

# Ensure data directory exists
DEFAULT_DATA_DIR.mkdir(exist_ok=True)
