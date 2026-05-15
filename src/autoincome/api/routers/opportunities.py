"""Opportunity CRUD API with AI-powered analysis.

Integrates real LLM-based content analysis, semantic deduplication,
and intelligent recommendation into the scan and retrieval pipeline.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.schemas.models import OpportunityCreate, OpportunityResponse, ScanResult
from autoincome.core.ai.content_analyzer import ContentAnalyzer
from autoincome.core.ai.recommender import AIRecommender
from autoincome.core.ai.semantic_dedup import SemanticDeduplicator
from autoincome.core.analyzer.scorer import Scorer
from autoincome.core.config import get_settings
from autoincome.core.database import OpportunityModel, ScanLogModel, get_db
from autoincome.core.logging_config import get_logger
from autoincome.core.security import generate_id
from autoincome.core.spiders.v2ex import V2EXSpider
from autoincome.core.spiders.zhihu import ZhihuSpider
from autoincome.core.spiders.github import GitHubSpider

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])
logger = get_logger(__name__)


@router.get("", response_model=list[OpportunityResponse])
async def list_opportunities(
    min_score: float = Query(default=7.0, ge=0.0, le=10.0),
    max_results: int = Query(default=20, ge=1, le=100),
    tag: str | None = Query(default=None, max_length=64),
    db: AsyncSession = Depends(get_db),
):
    """List opportunities with optional filtering."""
    stmt = (
        select(OpportunityModel)
        .where(OpportunityModel.score_total >= min_score)
        .order_by(OpportunityModel.score_total.desc())
        .limit(max_results)
    )
    if tag:
        stmt = stmt.where(OpportunityModel.tags.contains([tag]))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{opp_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opp_id: str = Path(..., min_length=1, max_length=64),
    db: AsyncSession = Depends(get_db),
):
    """Get a single opportunity by ID."""
    result = await db.execute(
        select(OpportunityModel).where(OpportunityModel.id == opp_id)
    )
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp


@router.post("", response_model=OpportunityResponse, status_code=201)
async def create_opportunity(
    payload: OpportunityCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new opportunity with AI analysis."""
    # Try AI analysis first
    analyzer = ContentAnalyzer()
    ai_result = await analyzer.analyze(payload.title, payload.description)

    # Blend AI scores with rule-based scores
    scorer = Scorer()
    score = scorer.score(payload.model_dump())

    opp = OpportunityModel(
        id=generate_id(),
        title=payload.title,
        description=ai_result.get("summary") or payload.description,
        time_investment=ai_result.get("time_investment", payload.time_investment),
        expected_income=payload.expected_income,
        source=payload.source,
        source_url=payload.source_url,
        verified=int(payload.verified),
        warning=ai_result.get("warning", payload.warning),
        tags=ai_result.get("tags", payload.tags),
        score_total=round(
            (score.total + sum([
                ai_result.get("score_feasibility", 5.0),
                ai_result.get("score_timeliness", 5.0),
                ai_result.get("score_credibility", 5.0),
                ai_result.get("score_roi", 5.0),
                ai_result.get("score_replicability", 5.0),
            ]) / 5.0 * 10) / 2, 1
        ),
        score_feasibility=round((score.feasibility + ai_result.get("score_feasibility", 5.0)) / 2, 1),
        score_timeliness=round((score.timeliness + ai_result.get("score_timeliness", 5.0)) / 2, 1),
        score_credibility=round((score.credibility + ai_result.get("score_credibility", 5.0)) / 2, 1),
        score_roi=round((score.roi + ai_result.get("score_roi", 5.0)) / 2, 1),
        score_replicability=round((score.replicability + ai_result.get("score_replicability", 5.0)) / 2, 1),
    )
    db.add(opp)
    await db.flush()
    return opp


@router.post("/scan", response_model=ScanResult)
async def run_scan(
    sources: list[str] | None = None,
    min_score: float = Query(default=7.0, ge=0.0, le=10.0),
    max_results: int = Query(default=10, ge=1, le=100),
    use_ai: bool = Query(default=True, description="Use AI analysis and semantic dedup"),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a full scan with AI-powered analysis and semantic deduplication."""
    start = time.time()
    all_items: list[dict[str, Any]] = []

    spider_registry = {
        "v2ex": V2EXSpider,
        "zhihu": ZhihuSpider,
        "github": GitHubSpider,
    }

    target_sources = sources or list(spider_registry.keys())

    for source in target_sources:
        spider_cls = spider_registry.get(source)
        if not spider_cls:
            continue
        try:
            spider = spider_cls()
            items = await spider.fetch(limit=20)
            logger.info("spider_fetched", source=source, count=len(items))
            all_items.extend(items)
        except Exception as exc:
            logger.warning("spider_fetch_failed", source=source, error=str(exc))

    # AI Content Analysis
    if use_ai and all_items:
        analyzer = ContentAnalyzer()
        analyzed_items = []
        for item in all_items:
            try:
                ai_result = await analyzer.analyze(
                    item.get("title", ""), item.get("description", "")
                )
                item.update(ai_result)
                # Blend scores
                base_score = item.get("score", 5.0)
                ai_avg = sum([
                    ai_result.get("score_feasibility", 5.0),
                    ai_result.get("score_timeliness", 5.0),
                    ai_result.get("score_credibility", 5.0),
                    ai_result.get("score_roi", 5.0),
                    ai_result.get("score_replicability", 5.0),
                ]) / 5.0
                item["score"] = round((base_score + ai_avg * 10) / 2, 1)
                analyzed_items.append(item)
            except Exception as exc:
                logger.debug("ai_analysis_item_failed", error=str(exc))
                analyzed_items.append(item)
        all_items = analyzed_items

    # Semantic Deduplication
    if use_ai:
        dedup = SemanticDeduplicator()
        unique, merged = await dedup.deduplicate(all_items)
    else:
        from autoincome.core.aggregator.deduplicator import Deduplicator
        dedup = Deduplicator()
        unique, merged = dedup.deduplicate(all_items)

    # Scoring and filtering
    scorer = Scorer()
    scored = []
    for item in unique[:100]:
        s = scorer.score(item)
        if s.total >= min_score:
            item["score_total"] = s.total
            item["score_feasibility"] = s.feasibility
            item["score_timeliness"] = s.timeliness
            item["score_credibility"] = s.credibility
            item["score_roi"] = s.roi
            item["score_replicability"] = s.replicability
            scored.append(item)

    # AI Personalized Recommendations (if user profile available)
    user_profile = {"skills": ["写作", "编程"], "time_budget": "2h", "risk_level": "moderate"}
    if use_ai and scored:
        try:
            recommender = AIRecommender()
            scored = await recommender.recommend(user_profile, scored, top_n=len(scored))
        except Exception as exc:
            logger.warning("ai_recommend_failed", error=str(exc))

    elapsed = time.time() - start

    # Persist scan log
    log = ScanLogModel(
        source=",".join(target_sources),
        raw_count=len(all_items),
        unique_count=len(unique),
        merged_count=merged,
        valid_count=len(scored),
        recommended_count=min(max_results, len(scored)),
        elapsed_seconds=elapsed,
    )
    db.add(log)

    # Build response
    from datetime import datetime, timezone
    opportunity_responses = []
    for item in scored[:max_results]:
        opp = {
            "id": item.get("id", generate_id()),
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "time_investment": item.get("time_investment", "2h/天"),
            "expected_income": item.get("expected_income", "未知"),
            "source": item.get("source", ""),
            "source_url": item.get("source_url"),
            "verified": bool(item.get("verified", False)),
            "warning": item.get("warning"),
            "tags": item.get("tags", []),
            "score_total": item.get("score_total", 5.0),
            "score_feasibility": item.get("score_feasibility", 0.0),
            "score_timeliness": item.get("score_timeliness", 0.0),
            "score_credibility": item.get("score_credibility", 0.0),
            "score_roi": item.get("score_roi", 0.0),
            "score_replicability": item.get("score_replicability", 0.0),
            "match_score": item.get("match_score"),
            "match_reasons": item.get("match_reasons", []),
            "risk_note": item.get("risk_note"),
            "merge_count": item.get("merge_count", 1),
            "created_at": datetime.now(timezone.utc),
        }
        opportunity_responses.append(opp)

    return ScanResult(
        status="success" if all_items else "partial",
        raw_count=len(all_items),
        unique_count=len(unique),
        merged_count=merged,
        valid_count=len(scored),
        recommended_count=min(max_results, len(scored)),
        elapsed_seconds=round(elapsed, 2),
        opportunities=opportunity_responses,
        error_message=None if all_items else "部分数据源不可用",
    )