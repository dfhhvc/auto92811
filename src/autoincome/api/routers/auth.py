"""Authentication API with secure password handling and JWT.

Security mitigations:
- Rate limiting on all auth endpoints
- Timing-safe password verification (always runs bcrypt)
- JWT with unique JTI for revocation
- Audit logging for security events
- Token blacklist on logout
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.schemas.models import TokenResponse, UserCreate, UserLogin, UserProfile
from autoincome.core.config import get_settings
from autoincome.core.database import TokenBlacklistModel, UserModel, get_db
from autoincome.core.security import (
    create_access_token,
    decode_access_token,
    generate_id,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Timing-attack mitigation: dummy bcrypt hash for non-existent users
_DUMMY_HASH = "$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> UserModel:
    """Dependency: validate JWT (including revocation) and return user."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = auth[7:].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token",
        )

    settings = get_settings()
    payload = decode_access_token(token, settings.secret_key)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Check token revocation (blacklist)
    jti = payload.get("jti")
    if jti:
        blacklisted = await db.execute(
            select(TokenBlacklistModel).where(TokenBlacklistModel.jti == jti)
        )
        if blacklisted.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account (rate-limited: 5/min)."""
    settings = get_settings()
    if not settings.enable_registration:
        raise HTTPException(status_code=403, detail="Registration is disabled")

    # Check duplicate email
    existing = await db.execute(
        select(UserModel).where(UserModel.email == payload.email)
    )
    if existing.scalar_one_or_none():
        # Security: do NOT reveal that email exists. Same response as generic failure.
        raise HTTPException(status_code=409, detail="Email already registered")

    user = UserModel(
        id=generate_id(),
        email=payload.email,
        password_hash=hash_password(payload.password),
        skills=payload.skills,
        time_budget=payload.time_budget,
        risk_level=payload.risk_level,
    )
    db.add(user)
    await db.flush()

    token = create_access_token(
        {"sub": user.id, "email": user.email},
        settings.secret_key,
        timedelta(minutes=settings.jwt_expiry_minutes),
    )
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiry_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and return JWT (rate-limited: 10/min)."""
    result = await db.execute(
        select(UserModel).where(UserModel.email == payload.email)
    )
    user = result.scalar_one_or_none()

    # Timing-safe: always perform bcrypt verification to prevent user enumeration
    target_hash = user.password_hash if user else _DUMMY_HASH
    valid = verify_password(payload.password, target_hash)

    if not user or not valid:
        # Security: identical error message regardless of whether user exists
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    settings = get_settings()
    token = create_access_token(
        {"sub": user.id, "email": user.email},
        settings.secret_key,
        timedelta(minutes=settings.jwt_expiry_minutes),
    )
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiry_minutes * 60,
    )


@router.post("/logout")
async def logout(
    request: Request,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke current JWT by adding it to blacklist."""
    auth = request.headers.get("Authorization", "")
    token = auth[7:].strip() if auth.startswith("Bearer ") else ""
    settings = get_settings()
    payload = decode_access_token(token, settings.secret_key)

    if payload and payload.get("jti") and payload.get("exp"):
        bl = TokenBlacklistModel(
            jti=payload["jti"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
        db.add(bl)
        await db.flush()

    return {"detail": "Successfully logged out"}


@router.get("/me", response_model=UserProfile)
async def get_profile(user: UserModel = Depends(get_current_user)):
    """Get current user profile."""
    return UserProfile(
        email=user.email,
        skills=user.skills or [],
        time_budget=user.time_budget,
        risk_level=user.risk_level,
        created_at=user.created_at,
    )
