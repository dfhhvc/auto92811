"""Community verification API - user voting and feedback."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.routers.auth import get_current_user
from autoincome.core.database import (
    CommunityVoteModel,
    OpportunityModel,
    UserModel,
    get_db,
)

router = APIRouter(prefix="/community", tags=["Community"])


@router.post("/vote/{opp_id}")
async def vote_opportunity(
    opp_id: str,
    vote: int,  # 1 or -1
    comment: str | None = None,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Vote on an opportunity's authenticity/helpfulness."""
    if vote not in (1, -1):
        raise HTTPException(status_code=400, detail="Vote must be 1 (up) or -1 (down)")

    # Check opportunity exists
    result = await db.execute(
        select(OpportunityModel).where(OpportunityModel.id == opp_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # Check if user already voted
    existing = await db.execute(
        select(CommunityVoteModel).where(
            CommunityVoteModel.opportunity_id == opp_id,
            CommunityVoteModel.user_id == user.id,
        )
    )
    existing_vote = existing.scalar_one_or_none()

    if existing_vote:
        existing_vote.vote = vote
        existing_vote.comment = comment or existing_vote.comment
    else:
        vote_record = CommunityVoteModel(
            opportunity_id=opp_id,
            user_id=user.id,
            vote=vote,
            comment=comment,
        )
        db.add(vote_record)

    await db.flush()

    # Recalculate community score
    votes = await db.execute(
        select(func.sum(CommunityVoteModel.vote)).where(
            CommunityVoteModel.opportunity_id == opp_id
        )
    )
    total_score = votes.scalar() or 0

    return {
        "opportunity_id": opp_id,
        "your_vote": vote,
        "community_score": total_score,
        "message": "Vote recorded",
    }


@router.get("/votes/{opp_id}")
async def get_votes(
    opp_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get community votes for an opportunity."""
    result = await db.execute(
        select(func.sum(CommunityVoteModel.vote)).where(
            CommunityVoteModel.opportunity_id == opp_id
        )
    )
    total = result.scalar() or 0

    count_result = await db.execute(
        select(func.count(CommunityVoteModel.id)).where(
            CommunityVoteModel.opportunity_id == opp_id
        )
    )
    vote_count = count_result.scalar() or 0

    comments_result = await db.execute(
        select(CommunityVoteModel).where(
            CommunityVoteModel.opportunity_id == opp_id,
            CommunityVoteModel.comment.isnot(None),
        )
    )
    comments = comments_result.scalars().all()

    return {
        "opportunity_id": opp_id,
        "total_score": total,
        "vote_count": vote_count,
        "comments": [
            {"user_id": c.user_id, "vote": c.vote, "comment": c.comment}
            for c in comments
        ],
    }
