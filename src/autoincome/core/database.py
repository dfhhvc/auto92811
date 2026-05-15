"""Production-grade PostgreSQL database layer with connection pooling.

Migrates from SQLite (v3) to PostgreSQL (v4) with:
- Asyncpg engine with connection pooling
- Alembic migrations (schema version control)
- Retry logic for transient failures
- SQLAlchemy 2.0 async ORM
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from sqlalchemy import NullPool
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
