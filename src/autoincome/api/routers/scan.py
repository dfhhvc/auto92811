"""Scan trigger endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.schemas.models import ScanResult
from autoincome.core.database import get_db

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.post("", response_model=ScanResult)
async def trigger_scan(db: AsyncSession = Depends(get_db)):
    """Trigger an on-demand scan (admin only in production)."""
    # Delegated to opportunities router for shared logic
    from autoincome.api.routers.opportunities import run_scan

    return await run_scan(db=db)
