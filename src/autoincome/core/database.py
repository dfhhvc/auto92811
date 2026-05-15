"""Async SQLite database layer with all models."""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from autoincome.core.config import get_settings

Base = declarative_base()


class OpportunityModel(Base):
    __tablename__ = "opportunities"

    id = Column(String(32), primary_key=True, index=True)
    title = Column(String(256), nullable=False, index=True)
    description = Column(Text, nullable=False)
    time_investment = Column(String(64), nullable=False)
    expected_income = Column(String(128), nullable=False)
    source = Column(String(128), nullable=False, index=True)
    source_url = Column(String(2048), nullable=True)
    verified = Column(Integer, default=0)
    warning = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    score_total = Column(Float, nullable=False, index=True)
    score_feasibility = Column(Float, default=0.0)
    score_timeliness = Column(Float, default=0.0)
    score_credibility = Column(Float, default=0.0)
    score_roi = Column(Float, default=0.0)
    score_replicability = Column(Float, default=0.0)
    match_score = Column(Float, nullable=True)
    merge_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    skills = Column(JSON, default=list)
    time_budget = Column(String(16), default="2h")
    risk_level = Column(String(16), default="moderate")
    languages = Column(JSON, default=lambda: ["zh"])
    is_active = Column(Integer, default=1)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)


class ScanLogModel(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(128), nullable=False)
    raw_count = Column(Integer, default=0)
    unique_count = Column(Integer, default=0)
    merged_count = Column(Integer, default=0)
    valid_count = Column(Integer, default=0)
    recommended_count = Column(Integer, default=0)
    elapsed_seconds = Column(Float, default=0.0)
    status = Column(String(32), default="success")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TokenBlacklistModel(Base):
    __tablename__ = "token_blacklist"

    jti = Column(String(32), primary_key=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"TokenBlacklistModel(jti=***{self.jti[-4:]}, expired={self.expires_at})"


class SecurityAuditLogModel(Base):
    __tablename__ = "security_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(64), nullable=False, index=True)
    user_id = Column(String(32), nullable=True, index=True)
    client_ip = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    details = Column(Text, nullable=True)
    success = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CommunityVoteModel(Base):
    """Community verification votes for opportunities."""

    __tablename__ = "community_votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(String(32), nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    vote = Column(Integer, nullable=False)  # 1=upvote, -1=downvote
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class IncomeRecordModel(Base):
    """User income tracking records."""

    __tablename__ = "income_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(32), nullable=False, index=True)
    opportunity_id = Column(String(32), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="CNY")
    description = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SpiderStatusModel(Base):
    """Spider execution status tracking."""

    __tablename__ = "spider_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spider_name = Column(String(64), nullable=False, index=True)
    status = Column(String(32), default="idle")
    last_run = Column(DateTime, nullable=True)
    last_success = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    total_runs = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── Engine & Session ──────────────────────────────────────────────

_async_engine: Any = None
_async_session: Any = None
_engine_lock = threading.Lock()
_session_lock = threading.Lock()


def get_async_engine():
    global _async_engine
    if _async_engine is None:
        with _engine_lock:
            if _async_engine is None:
                settings = get_settings()
                db_url = f"sqlite+aiosqlite:///{settings.db_path}"
                _async_engine = create_async_engine(
                    db_url,
                    echo=settings.debug,
                    pool_size=settings.db_pool_size,
                    max_overflow=10,
                )
    return _async_engine


def get_async_session() -> async_sessionmaker[AsyncSession]:
    global _async_session
    if _async_session is None:
        with _session_lock:
            if _async_session is None:
                _async_session = async_sessionmaker(
                    get_async_engine(),
                    class_=AsyncSession,
                    expire_on_commit=False,
                )
    return _async_session


async def init_db() -> None:
    settings = get_settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    async with get_async_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncIterator[AsyncSession]:
    session = get_async_session()()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def log_security_event(
    db: AsyncSession,
    event_type: str,
    user_id: str | None = None,
    client_ip: str | None = None,
    user_agent: str | None = None,
    details: str | None = None,
    success: bool = True,
) -> None:
    log = SecurityAuditLogModel(
        event_type=event_type,
        user_id=user_id,
        client_ip=(client_ip or "")[:64],
        user_agent=(user_agent or "")[:512],
        details=details,
        success=int(success),
    )
    db.add(log)
