"""
User Preferences Models

Pydantic models for user preferences.
"""

from pydantic import BaseModel, Field
from typing import List


class UserPreferences(BaseModel):
    """User preferences model."""

    user_id: int
    show_unspecified: bool = Field(
        default=True, description="Show 'unspecified' art styles in dashboard"
    )
    my_prompts_only: bool = Field(
        default=False, description="Show only my prompts by default"
    )
    excluded_tags: List[str] = Field(
        default=["high quality", "masterpiece", "best quality"],
        description="Tags to exclude from dashboard visualizations",
    )


class UserPreferencesUpdate(BaseModel):
    """User preferences update model."""

    show_unspecified: bool | None = None
    my_prompts_only: bool | None = None
    excluded_tags: List[str] | None = None


class UserPreferencesResponse(BaseModel):
    """User preferences response model."""

    user_id: int
    show_unspecified: bool
    my_prompts_only: bool
    excluded_tags: List[str]
