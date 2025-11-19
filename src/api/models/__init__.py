"""
API Models

Pydantic models for request/response validation.
"""

from .prompt_models import (
    PromptBase,
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptListResponse,
    PromptSearchRequest,
    PromptModelListResponse,
)

from .catalog_models import (
    Character,
    CharacterHair,
    CharacterEyes,
    Pose,
    Clothing,
    Setting,
    Lighting,
    ArtStyle,
    Technical,
    NSFWContent,
    SexualContent,
    Relationships,
    References,
    CameraComposition,
    MoodAtmosphere,
    Categories,
    Metadata,
    CatalogEntry,
    CatalogResponse,
    CatalogUpdateRequest,
    CatalogSearchRequest,
    CatalogSearchResponse,
    StatsResponse,
)

__all__ = [
    "PromptBase",
    "PromptCreate",
    "PromptUpdate",
    "PromptResponse",
    "PromptListResponse",
    "PromptSearchRequest",
    "PromptModelListResponse",
    "Character",
    "CharacterHair",
    "CharacterEyes",
    "Categories",
    "CatalogEntry",
    "CatalogResponse",
    "CatalogSearchRequest",
    "CatalogSearchResponse",
    "StatsResponse",
]
