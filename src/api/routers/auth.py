"""
Authentication Router

Endpoints for user authentication.
"""

from fastapi import APIRouter, HTTPException, status
from ..models.auth_models import LoginRequest, LoginResponse
from ..auth import create_access_token
from datetime import timedelta
from ..config import settings

router = APIRouter()


# Simple in-memory user storage for demo
# In production, use a proper database
USERS_DB = {
    "test": {
        "id": 1,
        "username": "test",
        "password": "test",  # In production, use hashed passwords!
        "email": "test@example.com",
        "role": "user",  # FIXED: test is regular user, not admin
    },
    "admin": {
        "id": 2,
        "username": "admin",
        "password": "admin",  # In production, use hashed passwords!
        "email": "admin@example.com",
        "role": "admin",
    },
    "user": {
        "id": 3,
        "username": "user",
        "password": "user",  # In production, use hashed passwords!
        "email": "user@example.com",
        "role": "user",
    },
}


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint - authenticate user and return JWT token.

    Args:
        credentials: Username and password

    Returns:
        JWT token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user from database
    user = USERS_DB.get(credentials.username)

    # Verify user exists and password matches
    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    token_data = {"sub": user["username"], "user_id": user["id"], "role": user["role"]}

    access_token = create_access_token(
        data=token_data, expires_delta=timedelta(minutes=settings.jwt_expire_minutes)
    )

    # Return token and user info (without password)
    user_info = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    }

    return LoginResponse(access_token=access_token, token_type="bearer", user=user_info)


@router.get("/me")
async def get_current_user():
    """
    Get current user information.
    Requires JWT token authentication.

    This endpoint can be used to verify if a token is still valid.
    """
    # This would use verify_token dependency in production
    return {
        "message": "Token verification endpoint - implement with verify_token dependency"
    }
