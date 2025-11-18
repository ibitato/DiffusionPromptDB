"""
Pydantic models for media ingestion endpoints.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ImageIngestionResult(BaseModel):
    """Per-file result returned by the ingestion endpoint."""

    filename: str = Field(..., description="Original filename supplied by the client")
    status: Literal["created", "failed", "skipped"] = Field(
        ..., description="Outcome of the ingestion attempt"
    )
    detail: str = Field(..., description="Diagnostic or success message")
    prompt_id: Optional[int] = Field(
        None, description="ID of the prompt created for this image (if any)"
    )


class BatchImageIngestionResponse(BaseModel):
    """Aggregated response for bulk image ingestion."""

    created: int = Field(..., ge=0, description="Number of prompts created")
    failed: int = Field(..., ge=0, description="Number of files that failed processing")
    results: list[ImageIngestionResult] = Field(
        default_factory=list, description="Per-file breakdown"
    )
