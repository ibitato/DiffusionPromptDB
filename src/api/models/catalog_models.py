"""
Pydantic Models for Catalog

Request/response models for catalog endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Character models
class CharacterHair(BaseModel):
    colors: List[str] = []
    styles: List[str] = []
    lengths: List[str] = []


class CharacterEyes(BaseModel):
    colors: List[str] = []
    shapes: List[str] = []


class Character(BaseModel):
    number_of_people: int = 0
    genders: List[str] = []
    age_ranges: List[str] = []
    body_types: List[str] = []
    hair: CharacterHair = CharacterHair()
    eyes: CharacterEyes = CharacterEyes()
    skin_tones: List[str] = []
    facial_features: List[str] = []
    ethnicities: List[str] = []
    species: List[str] = []
    breast_size: str = "unspecified"
    physical_attributes: List[str] = []


# Other category models
class Pose(BaseModel):
    main_pose: Optional[str] = None
    body_position: Optional[str] = None
    view_angle: Optional[str] = None
    actions: List[str] = []


class Clothing(BaseModel):
    style: Optional[str] = None
    items: List[str] = []
    coverage: Optional[str] = None
    accessories: List[str] = []


class Setting(BaseModel):
    location_type: Optional[str] = None
    indoor_outdoor: Optional[str] = None
    specific_place: Optional[str] = None
    environment_details: List[str] = []


class Lighting(BaseModel):
    type: Optional[str] = None
    time_of_day: Optional[str] = None
    quality: List[str] = []


class ArtStyle(BaseModel):
    primary_style: Optional[str] = None
    quality_tags: List[str] = []
    technique: List[str] = []
    score_indicators: List[str] = []


class Technical(BaseModel):
    resolution: List[str] = []
    camera_settings: List[str] = []
    detail_level: List[str] = []


class NSFWContent(BaseModel):
    level: str = Field(..., pattern="^(safe|suggestive|explicit)$")
    elements: List[str] = []


class SexualContent(BaseModel):
    sexual_acts: List[str] = []
    sexual_positions: List[str] = []
    body_fluids: List[str] = []
    genital_visibility: Optional[str] = None
    fetishes: List[str] = []


class Relationships(BaseModel):
    interaction_type: Optional[str] = None
    relationship: Optional[str] = None
    pov_perspective: Optional[str] = None


class References(BaseModel):
    character_names: List[str] = []
    series_franchise: List[str] = []
    artist_references: List[str] = []


class CameraComposition(BaseModel):
    shot_type: Optional[str] = None
    camera_angle: Optional[str] = None
    focus_area: Optional[str] = None
    composition_notes: List[str] = []


class MoodAtmosphere(BaseModel):
    overall_mood: Optional[str] = None
    emotions: List[str] = []


# Complete categories model
class Categories(BaseModel):
    """All categories for a prompt."""
    character: Character
    pose: Pose
    clothing: Clothing
    setting: Setting
    lighting: Lighting
    art_style: ArtStyle
    technical: Technical
    nsfw_content: NSFWContent
    mood_atmosphere: MoodAtmosphere
    sexual_content: SexualContent = SexualContent()
    relationships: Relationships = Relationships()
    references: References = References()
    camera_composition: CameraComposition = CameraComposition()
    main_tags: List[str] = []


# Metadata
class Metadata(BaseModel):
    processed_at: datetime
    model_used: str
    processing_time_ms: Optional[int] = None
    tokens_used: dict = {}


# Catalog entry (full)
class CatalogEntry(BaseModel):
    """Complete catalog entry."""
    id: int
    original_prompt: str
    categories: Categories
    metadata: Metadata


class CatalogResponse(BaseModel):
    """Response with catalog data."""
    id: int
    original_prompt: str
    categories: Categories
    metadata: Metadata


class CatalogUpdateRequest(BaseModel):
    """Request to update catalog categories."""
    categories: Categories


class CatalogSearchRequest(BaseModel):
    """Advanced search request."""
    nsfw_level: Optional[str] = Field(None, pattern="^(safe|suggestive|explicit)$")
    number_of_people: Optional[int] = Field(None, ge=0)
    art_style: Optional[str] = None
    indoor_outdoor: Optional[str] = Field(None, pattern="^(indoor|outdoor|mixed|unclear)$")
    hair_color: Optional[str] = None
    tags: Optional[List[str]] = None
    has_references: Optional[bool] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class CatalogSearchResponse(BaseModel):
    """Response for catalog search."""
    total: int
    page: int
    page_size: int
    results: List[CatalogResponse]


class StatsResponse(BaseModel):
    """Statistics response."""
    total_prompts: int
    nsfw_distribution: dict
    top_tags: List[dict]
    top_art_styles: List[dict]
    character_distribution: dict
