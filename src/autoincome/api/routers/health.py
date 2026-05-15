"""Health check endpoint with real database connectivity verification."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.schemas.models import HealthCheck
from autoincome.core.database import get_db

_start_time = time.time()

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheck)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Return service health status with real DB verification."""
    db_status = "disconnected"
    try:
        # Real DB connectivity check: execute a simple query
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_status = "connected"
    except Exception:
        db_status = "error"

    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        uptime_seconds=round(time.time() - _start_time, 2),
        database=db_status,
    )
