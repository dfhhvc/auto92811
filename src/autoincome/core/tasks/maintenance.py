"""Celery scheduled tasks for system maintenance.

Periodic jobs:
- Clean expired token blacklist entries
- Archive old scan logs
- Refresh cache statistics
- Database vacuum (PostgreSQL)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text

from autoincome.core.cache import cache
from autoincome.core.database import get_db_session
from autoincome.core.logging_config import get_logger
from autoincome.core.tasks import celery_app

logger = get_logger(__name__)


@celery_app.task
def cleanup_expired_tokens() -> dict[str, Any]:
    """Remove expired JWT blacklist entries."""
    import asyncio

    return asyncio.run(_cleanup_tokens_async())


async def _cleanup_tokens_async() -> dict[str, Any]:
    """Async implementation of token cleanup."""
    from autoincome.core.database import Base

    async with get_db_session() as db:
        # Delete tokens expired more than 7 days ago
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        result = await db.execute(
            text("""
                DELETE FROM token_blacklist
                WHERE expires_at < :cutoff
            """),
            {"cutoff": cutoff},
        )
        deleted = result.rowcount if result else 0

        logger.info("tokens_cleaned", deleted=deleted)
        return {"deleted": deleted}


@celery_app.task
def cleanup_old_scan_logs(days: int = 30) -> dict[str, Any]:
    """Archive scan logs older than N days."""
    import asyncio

    return asyncio.run(_cleanup_logs_async(days))


async def _cleanup_logs_async(days: int) -> dict[str, Any]:
    """Async implementation of log cleanup."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    async with get_db_session() as db:
        result = await db.execute(
            text("""
                DELETE FROM scan_logs
                WHERE created_at < :cutoff
            """),
            {"cutoff": cutoff},
        )
        deleted = result.rowcount if result else 0

        logger.info("scan_logs_cleaned", deleted=deleted, older_than_days=days)
        return {"deleted": deleted, "older_than_days": days}


@celery_app.task
def refresh_cache_stats() -> dict[str, Any]:
    """Log current cache statistics."""
    import asyncio

    return asyncio.run(_cache_stats_async())


async def _cache_stats_async() -> dict[str, Any]:
    """Async implementation of cache stats."""
    stats = await cache.get_stats()
    logger.info("cache_stats", **stats)
    return stats


@celery_app.task
def database_maintenance() -> dict[str, Any]:
    """Run PostgreSQL maintenance (VACUUM ANALYZE)."""
    import asyncio

    return asyncio.run(_db_maintenance_async())


async def _db_maintenance_async() -> dict[str, Any]:
    """Async implementation of DB maintenance."""
    from autoincome.core.database import _db_manager

    async with _db_manager.engine.begin() as conn:
        # VACUUM ANALYZE for PostgreSQL
        await conn.execute(text("VACUUM ANALYZE"))

    logger.info("database_maintenance_completed")
    return {"status": "completed"}
