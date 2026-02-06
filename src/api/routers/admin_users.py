"""
Administrative endpoints for managing users.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import verify_admin
from ..db import (
    DatabaseConnection,
    IntegrityConstraintError,
    get_users_db,
)
from ..models.admin_user_models import (
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdate,
    AdminResetPasswordRequest,
)
from ..services import user_service

router = APIRouter()


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    auth: dict = Depends(verify_admin),
    db: DatabaseConnection = Depends(get_users_db),
):
    users = user_service.list_users(db)
    return {"users": users}


@router.post("/users", response_model=AdminUserResponse, status_code=201)
async def create_user(
    payload: AdminUserCreate,
    auth: dict = Depends(verify_admin),
    db: DatabaseConnection = Depends(get_users_db),
):
    user_service.enforce_password_policy(payload.password)
    hashed = user_service.hash_password(payload.password)
    try:
        cursor = db.execute(
            """
            INSERT INTO users (username, email, role, full_name, password_hash, password_last_changed)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (
                payload.username,
                payload.email,
                payload.role,
                payload.full_name,
                hashed,
                datetime.utcnow().isoformat(),
            ),
        )
        user_id = cursor.fetchone()["id"]
    except IntegrityConstraintError as exc:
        raise HTTPException(status_code=400, detail="Username or email already exists") from exc
    db.execute(
        "INSERT INTO user_password_history (user_id, password_hash, changed_at) VALUES (?, ?, ?)",
        (user_id, hashed, datetime.utcnow().isoformat()),
    )
    db.commit()
    user = user_service.get_user_by_id(db, user_id)
    return user_service.serialize_profile(user)


@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    auth: dict = Depends(verify_admin),
    db: DatabaseConnection = Depends(get_users_db),
):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.execute(
        """
        UPDATE users
        SET email = COALESCE(?, email),
            role = COALESCE(?, role),
            is_active = COALESCE(?, is_active),
            full_name = COALESCE(?, full_name),
            default_landing_page = COALESCE(?, default_landing_page)
        WHERE id = ?
        """,
        (
            payload.email,
            payload.role,
            payload.is_active,
            payload.full_name,
            payload.default_landing_page,
            user_id,
        ),
    )
    db.commit()
    updated = user_service.get_user_by_id(db, user_id)
    return user_service.serialize_profile(updated)


@router.put("/users/{user_id}/password")
async def admin_reset_password(
    user_id: int,
    payload: AdminResetPasswordRequest,
    auth: dict = Depends(verify_admin),
    db: DatabaseConnection = Depends(get_users_db),
):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_service.update_password(db, user_id, payload.new_password)
    return {"detail": "Password reset successfully"}


@router.delete("/users/{user_id}", status_code=204)
async def delete_user_account(
    user_id: int,
    auth: dict = Depends(verify_admin),
    db: DatabaseConnection = Depends(get_users_db),
):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    from ..services import account_service

    account_service.delete_user_account(user, db, reason="admin_delete")
    return None
