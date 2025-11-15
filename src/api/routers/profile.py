"""
User profile management endpoints.
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import verify_token
from ..db import get_users_db
from ..models.profile_models import (
    UserProfileResponse,
    UserProfileUpdate,
    PasswordChangeRequest,
    DefaultLandingUpdate,
    DeleteAccountRequest,
)
from ..services import user_service, account_service

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    auth: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_users_db),
):
    user = user_service.get_user_by_id(db, auth["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_service.serialize_profile(user)


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    payload: UserProfileUpdate,
    auth: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_users_db),
):
    user = user_service.get_user_by_id(db, auth["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.execute(
        """
        UPDATE users SET full_name = ?, avatar_url = ?, location = ?, language = ?
        WHERE id = ?
        """,
        (
            payload.full_name,
            str(payload.avatar_url) if payload.avatar_url else None,
            payload.location,
            payload.language or user.get("language"),
            user["id"],
        ),
    )
    db.commit()
    updated = user_service.get_user_by_id(db, user["id"])
    return user_service.serialize_profile(updated)


@router.put("/profile/password")
async def change_password(
    payload: PasswordChangeRequest,
    auth: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_users_db),
):
    user = user_service.get_user_by_id(db, auth["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user_service.verify_password(payload.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user_service.update_password(db, user["id"], payload.new_password)
    return {"detail": "Password updated successfully"}


@router.put("/profile/default-page", response_model=UserProfileResponse)
async def update_default_landing(
    payload: DefaultLandingUpdate,
    auth: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_users_db),
):
    user = user_service.get_user_by_id(db, auth["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.execute(
        "UPDATE users SET default_landing_page=? WHERE id=?",
        (payload.default_landing_page, user["id"]),
    )
    db.commit()
    updated = user_service.get_user_by_id(db, user["id"])
    return user_service.serialize_profile(updated)


@router.delete("/account")
async def delete_account(
    payload: DeleteAccountRequest,
    auth: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_users_db),
):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="Deletion must be confirmed")

    user = user_service.get_user_by_id(db, auth["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user_service.verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Password is incorrect")

    dump_path = account_service.delete_user_account(user, db, payload.reason or "")

    return {"detail": "Account deleted", "dump_path": dump_path}
