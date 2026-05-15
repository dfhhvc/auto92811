"""Authentication API with secure password handling and JWT.

White-hat security layers:
- Rate limiting on all auth endpoints
- Timing-safe password verification (always runs bcrypt)
- JWT with unique JTI for revocation (minimal payload: sub only)
- Token blacklist on logout
- Identical error messages to prevent user enumeration
- Security audit logging for every auth event
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.schemas.models import TokenResponse, UserCreate, UserLogin, UserProfile
from autoincome.core.config import get_settings
from autoincome.core.database import (
    TokenBlacklistModel,
    UserModel,
    get_db,
    log_security_event,
)
from autoincome.core.rate_limit import limiter
from autoincome.core.security import (
    create_access_token,
    decode_access_token,
    generate_id,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pre-computed bcrypt hash for timing-attack mitigation.
_DUMMY_HASH = hash_password("dummy-" + generate_id()[:16])


def _get_client_ip(request: Request) -> str:
    """Extract real client IP, respecting X-Forwarded-For behind proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return "unknown"


def _get_user_agent(request: Request) -> str:
    """Extract User-Agent header."""
    return request.headers.get("User-Agent", "")


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
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    settings = get_settings()
    if not settings.enable_registration:
        raise HTTPException(status_code=403, detail="Registration is disabled")

    # Check duplicate email
    existing = await db.execute(
        select(UserModel).where(UserModel.email == payload.email)
    )
    if existing.scalar_one_or_none():
        # White-hat: audit log the failed attempt (without leaking to client)
        await log_security_event(
            db=db,
            event_type="registration_failed_duplicate",
            client_ip=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"Attempted registration with existing email domain: {payload.email.split('@')[-1]}",
            success=False,
        )
        raise HTTPException(status_code=409, detail="Registration failed")

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
        {"sub": user.id},
        settings.secret_key,
        timedelta(minutes=settings.jwt_expiry_minutes),
    )

    # White-hat: audit log successful registration
    await log_security_event(
        db=db,
        event_type="registration_success",
        user_id=user.id,
        client_ip=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details="User registered successfully",
        success=True,
    )

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiry_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and return JWT."""
    result = await db.execute(
        select(UserModel).where(UserModel.email == payload.email)
    )
    user = result.scalar_one_or_none()

    # Timing-safe: always perform bcrypt verification to prevent user enumeration
    target_hash = user.password_hash if user else _DUMMY_HASH
    valid = verify_password(payload.password, target_hash)

    client_ip = _get_client_ip(request)
    user_agent = _get_user_agent(request)

    if not user or not valid:
        # White-hat: audit log failed login attempt for intrusion detection
        await log_security_event(
            db=db,
            event_type="login_failed",
            user_id=user.id if user else None,
            client_ip=client_ip,
            user_agent=user_agent,
            details="Invalid credentials",
            success=False,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    settings = get_settings()
    token = create_access_token(
        {"sub": user.id},
        settings.secret_key,
        timedelta(minutes=settings.jwt_expiry_minutes),
    )

    # White-hat: audit log successful login
    await log_security_event(
        db=db,
        event_type="login_success",
        user_id=user.id,
        client_ip=client_ip,
        user_agent=user_agent,
        details="User authenticated successfully",
        success=True,
    )

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiry_minutes * 60,
    )


@router.post("/logout")
@limiter.limit("20/minute")
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

    # White-hat: audit log logout
    await log_security_event(
        db=db,
        event_type="logout",
        user_id=user.id,
        client_ip=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details="User logged out",
        success=True,
    )

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
