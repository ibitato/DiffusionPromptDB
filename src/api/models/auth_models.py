"""
Authentication Models

Pydantic models for authentication endpoints.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request model."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3)


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str
    token_type: str = "bearer"
    user: dict


class User(BaseModel):
    """User model."""

    id: int
    username: str
    email: str | None = None
    role: str = "user"
