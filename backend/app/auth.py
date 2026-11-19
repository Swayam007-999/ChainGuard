"""Authentication utilities for ChainGuard backend.

Supports:
1. X-ChainGuard-Key header verification for extension and log agent (constant-time).
2. JWT-based operator authentication stored in an HttpOnly, SameSite=Strict cookie.
"""

import hmac
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Cookie, Header, HTTPException, Request, status

from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours


def constant_time_compare(val1: str, val2: str) -> bool:
    """Compare two strings using constant-time comparison to prevent timing attacks."""
    if not val1 or not val2:
        return False
    return hmac.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Encode a JWT payload signed with the secret key."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please log in again.",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc


def require_api_key(
    x_chainguard_key: str | None = Header(None, alias="X-ChainGuard-Key"),
) -> str:
    """Dependency verifying the presence and validity of X-ChainGuard-Key header."""
    if not x_chainguard_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required X-ChainGuard-Key header",
        )
    if not constant_time_compare(x_chainguard_key, settings.CHAINGUARD_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_chainguard_key


def require_admin(
    access_token: str | None = Cookie(None, alias="access_token"),
) -> dict:
    """Dependency verifying the admin JWT stored in HttpOnly cookie."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
        )
    payload = decode_access_token(access_token)
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for operator action.",
        )
    return payload


def require_admin_or_api_key(
    request: Request,
    x_chainguard_key: str | None = Header(None, alias="X-ChainGuard-Key"),
    access_token: str | None = Cookie(None, alias="access_token"),
) -> str:
    """Allows either valid API key or valid admin session cookie."""
    if x_chainguard_key and constant_time_compare(x_chainguard_key, settings.CHAINGUARD_API_KEY):
        return "api_key"
    if access_token:
        try:
            payload = decode_access_token(access_token)
            if payload.get("role") == "admin":
                return "admin_cookie"
        except HTTPException:
            pass
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid X-ChainGuard-Key header or admin session cookie required",
    )
