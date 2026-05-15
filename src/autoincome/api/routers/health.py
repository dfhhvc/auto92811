"""Health check endpoint with real database, cache, and AI verification."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.core.ai.llm_client import get_llm_client
from autoincome.core.cache import cache
from autoincome.core.captcha.solver import get_captcha_solver
from autoincome.core.database import get_db
from autoincome.core.logging_config import get_logger

logger = get_logger(__name__)
_start_time = time.time()

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Return comprehensive health status with DB, Redis, and AI verification."""
    # Database check
    db_status = "disconnected"
    db_latency = 0.0
    try:
        t0 = time.time()
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_status = "connected"
        db_latency = round((time.time() - t0) * 1000, 2)
    except Exception:
        db_status = "error"

    # Redis check
    redis_status = "disconnected"
    redis_latency = 0.0
    try:
        t0 = time.time()
        await cache.connect()
        pong = await cache.ping()
        if pong:
            redis_status = "connected"
        redis_latency = round((time.time() - t0) * 1000, 2)
    except Exception:
        redis_status = "error"

    # LLM check
    llm_status = "unavailable"
    llm_providers = {}
    try:
        llm = get_llm_client()
        llm_providers = llm.health_check()
        if any(llm_providers.values()):
            llm_status = "available"
    except Exception as exc:
        logger.debug("llm_health_check_failed", error=str(exc))

    # Captcha solver check
    captcha_status = get_captcha_solver().health_check()

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.now(timezone.utc),
        "uptime_seconds": round(time.time() - _start_time, 2),
        "version": "4.1.0",
        "database": {"status": db_status, "latency_ms": db_latency},
        "redis": {"status": redis_status, "latency_ms": redis_latency},
        "llm": {"status": llm_status, "providers": llm_providers},
        "captcha": captcha_status,
    }
