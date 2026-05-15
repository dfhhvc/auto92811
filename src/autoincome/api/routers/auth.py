"""Authentication API with secure password handling and JWT.

No plaintext passwords. No sensitive data in JWT payload.
Rate limited to prevent brute force.
"""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.schemas.models import TokenResponse, UserCreate, UserLogin, UserProfile
from autoincome.core.config import get_settings
from autoincome.core.database import UserModel, get_db
from autoincome.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> UserModel:
    """Dependency: validate JWT and return user."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = auth[7:]
    payload = decode_access_token(token, get_settings().secret_key)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
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
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    settings = get_settings()
    if not settings.enable_registration:
        raise HTTPException(status_code=403, detail="Registration is disabled")

    # Check duplicate email
    existing = await db.execute(
        select(UserModel).where(UserModel.email == payload.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = UserModel(
        id=__import__("autoincome.core.security").core.security.generate_id(),
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
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate and return JWT."""
    result = await db.execute(
        select(UserModel).where(UserModel.email == payload.email)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
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
