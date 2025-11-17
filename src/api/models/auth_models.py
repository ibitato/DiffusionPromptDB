"""
Authentication Models

Pydantic models for authentication endpoints.
"""

from pydantic import BaseModel, Field, EmailStr


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


class ExpiredPasswordChangeRequest(BaseModel):
    """Request payload for renewing an expired password during login."""

    username: str = Field(..., min_length=3, max_length=50)
    current_password: str = Field(..., min_length=3)
    new_password: str = Field(..., min_length=8)


class RegistrationRequest(BaseModel):
    """Request payload for new user registration."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class VerificationRequest(BaseModel):
    """Payload for completing email verification."""

    token: str = Field(..., min_length=20, max_length=128)
