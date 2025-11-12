"""
Data models for DiffusionPromptDB.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Prompt:
    """
    Represents a diffusion model prompt.
    
    Attributes:
        id: Unique identifier (auto-generated)
        text: The prompt text
        negative_prompt: Optional negative prompt
        model: Model name/identifier
        parameters: JSON string with generation parameters (cfg_scale, steps, etc.)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        tags: Comma-separated tags
        category: Category classification
        rating: Optional rating (1-5)
        notes: Additional notes
    """
    text: str
    negative_prompt: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[str] = None
    tags: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate rating if provided."""
        if self.rating is not None and not (1 <= self.rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
    
    def to_dict(self):
        """Convert prompt to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "negative_prompt": self.negative_prompt,
            "model": self.model,
            "parameters": self.parameters,
            "tags": self.tags,
            "category": self.category,
            "rating": self.rating,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
