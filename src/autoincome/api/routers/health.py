"""Health check endpoint (no auth required)."""

from __future__ import annotations

import time

from fastapi import APIRouter

from autoincome import __version__
from autoincome.api.schemas.models import HealthCheck

_start_time = time.time()

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Return service health status."""
    return HealthCheck(
        status="healthy",
        version=__version__,
        timestamp=__import__("datetime").datetime.utcnow(),
        uptime_seconds=round(time.time() - _start_time, 2),
        database="connected",
    )
