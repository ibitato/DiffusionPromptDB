"""
Authentication Router

Endpoints for user authentication with secure password hashing.
"""

from fastapi import APIRouter, HTTPException, status, Request
from ..models.auth_models import LoginRequest, LoginResponse
from ..auth import create_access_token
from ..security import hash_password, verify_password
from datetime import timedelta
from ..config import settings
from ..middleware.rate_limiting import limiter, get_rate_limit, get_rate_limit_message
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Secure user storage with hashed passwords
# NOTE: In production, these should be stored in a database
# Default passwords for demo accounts (using bcrypt):
# - test/test123
# - admin/admin123
# - user/user123
USERS_DB = {
    "test": {
        "id": 1,
        "username": "test",
        "password": "$2b$12$2kzH1zP2M0Z8hDIpJhKJa.GauoSacA.9BEjA7MmzSvlrrS4/Frj6C",  # test123
        "email": "test@example.com",
        "role": "user",
    },
    "admin": {
        "id": 2,
        "username": "admin",
        "password": "$2b$12$Bg6ffNq7J57yYtEpb5f6Y.BEcPNGVu21E0/UzPQN8Gd6.SPQuuoDy",  # admin123
        "email": "admin@example.com",
        "role": "admin",
    },
    "user": {
        "id": 3,
        "username": "user",
        "password": "$2b$12$FyZ3QuaSls8v1DQXn11uJ.X4H8ei7U7FbjuCbYD9Bv9QVIpq5OJzm",  # user123
        "email": "user@example.com",
        "role": "user",
    },
}


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")  # Strict rate limiting to prevent brute force
async def login(request: Request, credentials: LoginRequest):
    """
    Login endpoint - authenticate user and return JWT token.

    Uses bcrypt for secure password verification.
    Rate limited to 5 attempts per minute to prevent brute force attacks.

    Args:
        request: FastAPI request object (for rate limiting)
        credentials: Username and password

    Returns:
        JWT token and user information

    Raises:
        HTTPException: If credentials are invalid
        RateLimitExceeded: If too many login attempts
    """
    # Get user from database
    user = USERS_DB.get(credentials.username)

    if not user:
        # Log failed login attempt
        logger.warning(f"Login attempt with unknown username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password using bcrypt
    if not verify_password(credentials.password, user["password"]):
        # Log failed login attempt
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful login
    logger.info(f"Successful login for user: {credentials.username}")

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
@limiter.limit("30/minute")  # Moderate rate limiting for token verification
async def get_current_user(request: Request):
    """
    Get current user information.
    Requires JWT token authentication.

    This endpoint can be used to verify if a token is still valid.
    Rate limited to 30 requests per minute.
    """
    # This would use verify_token dependency in production
    return {
        "message": "Token verification endpoint - implement with verify_token dependency"
    }
