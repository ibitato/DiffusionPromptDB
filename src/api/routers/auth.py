"""
Authentication Router

Handles login and token validation backed by users.db.
"""

from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..auth import create_access_token, verify_token
from ..config import settings
from ..db import DatabaseConnection, IntegrityConstraintError, get_users_db
from ..middleware.rate_limiting import limiter
from ..models.auth_models import (
    ExpiredPasswordChangeRequest,
    LoginRequest,
    LoginResponse,
    RegistrationRequest,
    VerificationRequest,
)
from ..services import email_service, user_service, verification_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_account(
    payload: RegistrationRequest,
    request: Request,
    db: DatabaseConnection = Depends(get_users_db),
):
    """Create a new user account pending email verification."""

    username = payload.username.strip()
    email = payload.email.lower().strip()

    user_service.enforce_password_policy(payload.password)

    existing = db.execute(
        "SELECT 1 FROM users WHERE username=? OR email=?", (username, email)
    ).fetchone()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    password_hash = user_service.hash_password(payload.password)
    now = datetime.utcnow().isoformat()
    try:
        cursor = db.execute(
            """
            INSERT INTO users (username, email, password_hash, role, is_active, must_change_password, password_last_changed)
            VALUES (?, ?, ?, 'user', ?, ?, ?)
            RETURNING id
            """,
            (username, email, password_hash, False, False, now),
        )
    except IntegrityConstraintError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        ) from exc
    user_id = cursor.fetchone()["id"]
    db.execute(
        """
        INSERT INTO user_preferences (user_id)
        VALUES (?)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id,),
    )
    db.commit()

    token, expires_at = verification_service.create_verification_token(db, user_id)
    email_sent = email_service.send_verification_email(email, token)
    logger.info(
        "Registration created for %s from %s",
        username,
        request.client.host if request.client else "unknown",
    )

    response = {
        "detail": "Registration successful. Check your email for the verification link.",
        "expires_at": expires_at,
    }
    if settings.email_debug_mode or not email_sent:
        response["verification_token"] = token
    else:
        response["verification_token"] = None

    if not email_sent:
        response[
            "warning"
        ] = "Email delivery is not configured; provide the token manually to verify."

    return response


@router.post("/verify")
@limiter.limit("10/minute")
async def verify_account(
    payload: VerificationRequest,
    request: Request,
    db: DatabaseConnection = Depends(get_users_db),
):
    """Complete account verification and enable login."""

    user_id = verification_service.consume_verification_token(db, payload.token)
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.execute(
        "UPDATE users SET is_active=? WHERE id=?",
        (True, user_id),
    )
    db.commit()
    logger.info("User %s verified their account", user.get("username"))
    return {"detail": "Account verified successfully. You can now sign in."}


@router.post("/login", response_model=LoginResponse)
@limiter.limit("20/minute")
async def login(
    request: Request,
    credentials: LoginRequest,
    db: DatabaseConnection = Depends(get_users_db),
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
        db.execute("UPDATE users SET must_change_password=? WHERE id=?", (True, user["id"]))
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


@router.post("/password/expired")
@limiter.limit("10/minute")
async def reset_expired_password(
    payload: ExpiredPasswordChangeRequest,
    request: Request,
    db: DatabaseConnection = Depends(get_users_db),
):
    """Allow users whose password expired to set a new one without an active session."""

    user = user_service.get_user_by_username(db, payload.username)
    if not user or not user_service.verify_password(
        payload.current_password, user["password_hash"]
    ):
        logger.warning(
            "Failed expired-password reset for %s from %s",
            payload.username,
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )

    if not user.get("is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled. Contact administrator.",
        )

    user_service.update_password(db, user["id"], payload.new_password)
    logger.info("User %s updated password via expired-password flow", payload.username)
    return {"detail": "Password updated. Please log in again."}


@router.get("/me", response_model=LoginResponse)
@limiter.limit("30/minute")
async def get_current_user(
    request: Request,
    token_payload: dict = Depends(verify_token),
    db: DatabaseConnection = Depends(get_users_db),
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
