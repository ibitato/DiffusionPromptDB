"""
DiffusionPromptDB REST API

Secure REST API for managing Stable Diffusion prompts and catalogation.
"""

__version__ = "1.0.0"
__author__ = "DiffusionPromptDB Team"

from .main import app

__all__ = ["app"]
