"""Admin API for managing the application."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.routers.auth import get_current_user
from autoincome.core.database import (
    OpportunityModel,
    ScanLogModel,
    SpiderStatusModel,
    UserModel,
    get_db,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


async def require_admin(
    user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Dependency to require admin privileges."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


@router.get("/stats")
async def get_stats(
    admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get application statistics."""
    user_count = await db.execute(select(func.count(UserModel.id)))
    users = user_count.scalar() or 0

    opp_count = await db.execute(select(func.count(OpportunityModel.id)))
    opps = opp_count.scalar() or 0

    scan_count = await db.execute(select(func.count(ScanLogModel.id)))
    scans = scan_count.scalar() or 0

    spider_result = await db.execute(select(SpiderStatusModel))
    spiders = spider_result.scalars().all()

    return {
        "users": users,
        "opportunities": opps,
        "scans": scans,
        "spiders": [
            {
                "name": s.spider_name,
                "status": s.status,
                "total_runs": s.total_runs,
                "success_count": s.success_count,
                "error_count": s.error_count,
                "last_run": s.last_run.isoformat() if s.last_run else None,
            }
            for s in spiders
        ],
    }


@router.post("/spiders/{spider_name}/trigger")
async def trigger_spider(
    spider_name: str,
    admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger a spider scan."""
    status = await db.execute(
        select(SpiderStatusModel).where(SpiderStatusModel.spider_name == spider_name)
    )
    spider = status.scalar_one_or_none()

    if not spider:
        spider = SpiderStatusModel(spider_name=spider_name)
        db.add(spider)
    else:
        spider.status = "triggered"

    await db.flush()

    return {
        "message": f"Spider {spider_name} triggered",
        "status": "triggered",
    }


@router.delete("/opportunities/{opp_id}")
async def delete_opportunity(
    opp_id: str,
    admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete an opportunity (admin only)."""
    result = await db.execute(
        select(OpportunityModel).where(OpportunityModel.id == opp_id)
    )
    opp = result.scalar_one_or_none()

    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    await db.delete(opp)
    await db.flush()

    return {"message": f"Opportunity {opp_id} deleted"}
