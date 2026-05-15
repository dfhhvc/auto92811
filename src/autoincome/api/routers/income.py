"""Income tracking API."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.routers.auth import get_current_user
from autoincome.core.database import IncomeRecordModel, OpportunityModel, UserModel, get_db

router = APIRouter(prefix="/income", tags=["Income"])


@router.post("/record")
async def record_income(
    opportunity_id: str,
    amount: float,
    currency: str = "CNY",
    description: str | None = None,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record income from an opportunity."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Verify opportunity exists
    opp = await db.execute(
        select(OpportunityModel).where(OpportunityModel.id == opportunity_id)
    )
    if not opp.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Opportunity not found")

    record = IncomeRecordModel(
        user_id=user.id,
        opportunity_id=opportunity_id,
        amount=amount,
        currency=currency.upper(),
        description=description,
    )
    db.add(record)
    await db.flush()

    return {
        "message": "Income recorded",
        "record_id": record.id,
        "amount": amount,
        "currency": currency,
    }


@router.get("/dashboard")
async def get_dashboard(
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's income dashboard."""
    # Total income
    total_result = await db.execute(
        select(func.sum(IncomeRecordModel.amount)).where(
            IncomeRecordModel.user_id == user.id
        )
    )
    total_income = total_result.scalar() or 0.0

    # Income by opportunity
    by_opp = await db.execute(
        select(
            IncomeRecordModel.opportunity_id,
            OpportunityModel.title,
            func.sum(IncomeRecordModel.amount),
            func.count(IncomeRecordModel.id),
        )
        .join(OpportunityModel, IncomeRecordModel.opportunity_id == OpportunityModel.id)
        .where(IncomeRecordModel.user_id == user.id)
        .group_by(IncomeRecordModel.opportunity_id)
    )

    opportunities = []
    for row in by_opp.all():
        opportunities.append({
            "opportunity_id": row[0],
            "title": row[1],
            "total": row[2],
            "records": row[3],
        })

    # Recent records
    recent = await db.execute(
        select(IncomeRecordModel)
        .where(IncomeRecordModel.user_id == user.id)
        .order_by(IncomeRecordModel.recorded_at.desc())
        .limit(10)
    )

    return {
        "total_income": total_income,
        "currency": "CNY",
        "opportunities_count": len(opportunities),
        "opportunities": opportunities,
        "recent_records": [
            {
                "id": r.id,
                "amount": r.amount,
                "currency": r.currency,
                "description": r.description,
                "date": r.recorded_at.isoformat(),
            }
            for r in recent.scalars().all()
        ],
    }
