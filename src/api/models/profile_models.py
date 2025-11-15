"""Pydantic models for user profile endpoints."""

from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, HttpUrl


LandingPage = Literal["dashboard", "search"]


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    location: Optional[str] = None
    language: str = "en"
    default_landing_page: LandingPage = "dashboard"
    must_change_password: bool = False
    password_last_changed: Optional[str] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    is_active: bool = True


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=120)
    avatar_url: Optional[HttpUrl] = None
    location: Optional[str] = Field(None, max_length=120)
    language: Optional[str] = Field(None, max_length=10)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class DefaultLandingUpdate(BaseModel):
    default_landing_page: LandingPage


class DeleteAccountRequest(BaseModel):
    password: str
    confirm: bool = False
    reason: Optional[str] = Field(None, max_length=200)
