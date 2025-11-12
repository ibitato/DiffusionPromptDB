"""
DiffusionPromptDB - A portable SQLite-based database for managing diffusion model prompts.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .database import Database
from .models import Prompt

__all__ = ["Database", "Prompt", "__version__"]
