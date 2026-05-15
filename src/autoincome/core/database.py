"""Production-grade PostgreSQL database layer with connection pooling.

Migrates from SQLite (v3) to PostgreSQL (v4) with:
- Asyncpg engine with connection pooling
- Alembic migrations (schema version control)
- Retry logic for transient failures
- SQLAlchemy 2.0 async ORM
- All data models
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from sqlalchemy import JSON, Column, DateTime, Float, Integer, NullPool, String, Text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from autoincome.core.config import get_settings

Base = declarative_base()


# ── Models ──────────────────────────────────────────────────────

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
    __tablename__ = "community_votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(String(32), nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    vote = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class IncomeRecordModel(Base):
    __tablename__ = "income_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(32), nullable=False, index=True)
    opportunity_id = Column(String(32), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="CNY")
    description = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SpiderStatusModel(Base):
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

# Module-level singletons (lazy-initialized)
_async_engine: Any = None
_async_session_factory: Any = None


class DatabaseManager:
    """Manages async PostgreSQL connections with pooling."""

    def __init__(self) -> None:
        self._engine = None
        self._session_factory = None

    async def initialize(self) -> None:
        """Create engine and session factory."""
        settings = get_settings()

        # Production: use real connection pool
        # Testing: use NullPool to avoid connection overhead
        poolclass = NullPool if settings.env == "testing" else None

        self._engine = create_async_engine(
            settings.db_url,
            echo=settings.debug,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,    # Recycle connections after 5min
            poolclass=poolclass,
            future=True,
        )

        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        # Create tables if they don't exist (development only)
        # Production uses Alembic migrations
        if settings.env in ("development", "testing"):
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Dispose engine and close all connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    @property
    def engine(self) -> Any:
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._session_factory


# Global singleton
_db_manager = DatabaseManager()


async def init_db() -> None:
    """Initialize database (called on app startup)."""
    await _db_manager.initialize()


async def close_db() -> None:
    """Close database connections (called on app shutdown)."""
    await _db_manager.close()


@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Get a database session with automatic commit/rollback."""
    session = _db_manager.session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency for database sessions."""
    async with get_db_session() as session:
        yield session


@retry(
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def execute_with_retry(session: AsyncSession, stmt: Any) -> Any:
    """Execute a SQL statement with retry logic for transient failures."""
    result = await session.execute(stmt)
    return result


async def log_security_event(
    db: AsyncSession,
    event_type: str,
    user_id: str | None = None,
    client_ip: str | None = None,
    user_agent: str | None = None,
    details: str | None = None,
    success: bool = True,
) -> None:
    """Log a security event to the audit log."""
    log = SecurityAuditLogModel(
        event_type=event_type,
        user_id=user_id,
        client_ip=(client_ip or "")[:64],
        user_agent=(user_agent or "")[:512],
        details=details,
        success=int(success),
    )
    db.add(log)
