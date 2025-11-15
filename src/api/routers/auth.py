"""
Authentication Router

Handles login and token validation backed by users.db.
"""

from datetime import datetime, timedelta
import logging
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..auth import create_access_token, verify_token
from ..config import settings
from ..db import get_users_db
from ..middleware.rate_limiting import limiter
from ..models.auth_models import LoginRequest, LoginResponse
from ..services import user_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: LoginRequest,
    db: sqlite3.Connection = Depends(get_users_db),
):
    """Authenticate user and return JWT."""
    user = user_service.get_user_by_username(db, credentials.username)

    if not user or not user_service.verify_password(
        credentials.password, user["password_hash"]
    ):
        logger.warning("Failed login attempt for user %s", credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled. Contact administrator.",
        )

    if user.get("must_change_password") or user_service.needs_password_rotation(user):
        db.execute("UPDATE users SET must_change_password=1 WHERE id=?", (user["id"],))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password expired. Please update your password.",
            headers={"X-Password-Expired": "true"},
        )

    token_payload = {"sub": user["username"], "user_id": user["id"], "role": user["role"]}
    access_token = create_access_token(
        data=token_payload, expires_delta=timedelta(minutes=settings.jwt_expire_minutes)
    )

    db.execute(
        "UPDATE users SET last_login=? WHERE id=?",
        (datetime.utcnow().isoformat(), user["id"]),
    )
    db.commit()

    profile = user_service.serialize_profile(user)
    return LoginResponse(access_token=access_token, token_type="bearer", user=profile)


@router.get("/me", response_model=LoginResponse)
@limiter.limit("30/minute")
async def get_current_user(
    request: Request,
    token_payload: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_users_db),
):
    """Return user info for the authenticated token."""
    user = user_service.get_user_by_id(db, token_payload["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    profile = user_service.serialize_profile(user)
    refreshed_token = create_access_token(
        data={"sub": profile["username"], "user_id": profile["id"], "role": profile["role"]},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )
    return LoginResponse(access_token=refreshed_token, token_type="bearer", user=profile)
