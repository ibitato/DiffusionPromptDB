"""Models for admin user management APIs."""

from typing import Optional, Literal, List
from pydantic import BaseModel, EmailStr, Field

RoleLiteral = Literal["admin", "user"]
LandingPage = Literal["dashboard", "search"]


class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    role: RoleLiteral = "user"
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleLiteral] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None
    default_landing_page: Optional[LandingPage] = None


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleLiteral
    is_active: bool
    created_at: Optional[str]
    last_login: Optional[str]
    default_landing_page: LandingPage


class AdminUserListResponse(BaseModel):
    users: List[AdminUserResponse]


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)
