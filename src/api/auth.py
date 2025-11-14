"""
Authentication and Authorization

Handles API key and JWT token authentication.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from .config import settings

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key for read-only access.

    Args:
        api_key: API key from header

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key is invalid
    """
    if api_key and api_key in settings.api_keys:
        return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
        headers={"WWW-Authenticate": "ApiKey"},
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def verify_token(token: str = Security(bearer_scheme)) -> dict:
    """
    Verify JWT token for write access.

    Args:
        token: JWT token from Authorization header

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional: Public access (no auth required)
def optional_auth(
    api_key: Optional[str] = Security(api_key_header),
    token: Optional[str] = Security(bearer_scheme),
) -> Optional[dict]:
    """
    Optional authentication - allows public or authenticated access.

    Returns:
        Auth info if provided, None if public access
    """
    if token:
        try:
            return verify_token(token)
        except HTTPException:
            pass

    if api_key and api_key in settings.api_keys:
        return {"type": "api_key", "key": api_key}

    return None  # Public access


def get_current_user_optional(token: Optional[str] = Security(bearer_scheme)) -> Optional[dict]:
    """
    Get current user from JWT token if provided, otherwise return None.
    Used for endpoints that work both authenticated and unauthenticated.

    Returns:
        User info from token if authenticated, None otherwise
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None


def verify_admin(auth: dict = Security(verify_token)) -> dict:
    """
    Verify that the user is an admin.

    Args:
        auth: Decoded token payload

    Returns:
        Auth payload if user is admin

    Raises:
        HTTPException: If user is not admin
    """
    if auth.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return auth


def verify_ownership_or_admin(prompt_id: int, auth: dict, db) -> bool:
    """
    Verify that user owns the prompt or is admin.

    Args:
        prompt_id: ID of the prompt
        auth: Decoded token payload
        db: Database connection

    Returns:
        True if user is owner or admin

    Raises:
        HTTPException: If user doesn't have access
    """
    user_id = auth.get("user_id")
    user_role = auth.get("role")
    
    # Admin can access everything
    if user_role == "admin":
        return True
    
    # Check ownership
    row = db.execute(
        "SELECT created_by FROM prompts WHERE id = ?",
        (prompt_id,)
    ).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    created_by = row[0]
    
    # NULL means preloaded (only admin can modify)
    if created_by is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify preloaded prompts. Admin privileges required."
        )
    
    # Check if user owns this prompt
    if created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own prompts"
        )
    
    return True


def can_modify_prompt(prompt_id: int, auth: dict, db) -> dict:
    """
    Check and verify if user can modify prompt.
    Helper that combines verification with the database connection.
    
    Args:
        prompt_id: ID of the prompt
        auth: Decoded token payload
        db: Database connection
        
    Returns:
        Auth dict if user has permission
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    verify_ownership_or_admin(prompt_id, auth, db)
    return auth
