"""
Pydantic Models for Prompts

Request/response models for prompt endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PromptBase(BaseModel):
    """Base prompt model."""

    text: str = Field(..., description="The prompt text", min_length=1)
    negative_prompt: Optional[str] = Field(None, description="Negative prompt")
    model: Optional[str] = Field(None, description="Model identifier")
    parameters: Optional[str] = Field(None, description="Generation parameters (JSON)")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    category: Optional[str] = Field(None, description="Category classification")
    art_style: Optional[str] = Field(
        None, description="Art style (anime, realistic, etc.)"
    )
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    notes: Optional[str] = Field(None, description="Additional notes")


class PromptCreate(PromptBase):
    """Model for creating a new prompt."""

    pass


class PromptUpdate(BaseModel):
    """Model for updating a prompt (all fields optional)."""

    text: Optional[str] = Field(None, min_length=1)
    negative_prompt: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[str] = None
    tags: Optional[str] = None
    category: Optional[str] = None
    art_style: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class PromptResponse(PromptBase):
    """Model for prompt responses."""

    id: int
    created_at: datetime
    updated_at: datetime
    image_path: Optional[str] = Field(
        None, description="Relative path to the stored source image"
    )
    thumbnail_path: Optional[str] = Field(
        None, description="Relative path to the generated thumbnail"
    )
    created_by: Optional[int] = Field(
        None, description="User ID of creator (NULL for preloaded)"
    )

    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    """Response model for list of prompts."""

    total: int
    page: int
    page_size: int
    results: list[PromptResponse]


class PromptSearchRequest(BaseModel):
    """Request model for searching prompts."""

    text: Optional[str] = Field(None, description="Search in prompt text")
    category: Optional[str] = Field(None, description="Filter by category")
    model: Optional[str] = Field(None, description="Filter by model")
    min_rating: Optional[int] = Field(None, ge=1, le=5, description="Minimum rating")
    tags: Optional[list[str]] = Field(None, description="Filter by tags")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PromptModelListResponse(BaseModel):
    """List of distinct models available for a user."""

    models: list[str]
