"""Scan trigger endpoint with spider registry."""

from __future__ import annotations

from datetime import datetime, timezone
import time

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from autoincome.api.routers.auth import get_current_user
from autoincome.api.schemas.models import ScanResult
from autoincome.core.aggregator.deduplicator import Deduplicator
from autoincome.core.analyzer.scorer import Scorer
from autoincome.core.database import (
    OpportunityModel,
    ScanLogModel,
    SpiderStatusModel,
    UserModel,
    get_db,
)
from autoincome.core.notifier.push import NotificationManager
from autoincome.core.security import generate_id
from autoincome.core.spiders import ALL_SPIDERS

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.post("", response_model=ScanResult)
async def trigger_scan(
    sources: list[str] | None = None,
    min_score: float = 7.0,
    max_results: int = 10,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a scan using all available spiders."""
    start = time.time()

    all_items = []
    spider_errors = []

    spider_names = sources or list(ALL_SPIDERS.keys())

    for name in spider_names:
        spider_class = ALL_SPIDERS.get(name)
        if not spider_class:
            spider_errors.append(f"Unknown spider: {name}")
            continue

        spider = spider_class()
        spider_status = None
        try:
            status_result = await db.execute(
                select(SpiderStatusModel).where(SpiderStatusModel.spider_name == name)
            )
            spider_status = status_result.scalar_one_or_none()
            if not spider_status:
                spider_status = SpiderStatusModel(spider_name=name)
                db.add(spider_status)

            spider_status.status = "running"
            spider_status.last_run = datetime.now(timezone.utc)
            spider_status.total_runs += 1

            items = await spider.fetch(limit=20)
            all_items.extend(items)

            spider_status.status = "idle"
            spider_status.last_success = datetime.now(timezone.utc)
            spider_status.success_count += 1

        except Exception as e:
            spider_errors.append(f"{name}: {str(e)}")
            if spider_status:
                spider_status.status = "error"
                spider_status.last_error = str(e)[:1024]
                spider_status.error_count += 1

    # Deduplicate
    dedup = Deduplicator()
    unique, merged = dedup.deduplicate(all_items)

    # Score
    scorer = Scorer()
    scored = []
    for item in unique:
        s = scorer.score(item)
        if s.total >= min_score:
            item["score"] = s.total
            scored.append(item)

    # Save to database
    saved_count = 0
    for item in scored[:max_results]:
        opp = OpportunityModel(
            id=generate_id(),
            title=item["title"],
            description=item["description"],
            time_investment=item.get("time_investment", "2h/天"),
            expected_income=item.get("expected_income", "未知"),
            source=item["source"],
            source_url=item.get("source_url"),
            verified=int(item.get("verified", False)),
            warning=item.get("warning"),
            tags=item.get("tags", []),
            score_total=item.get("score", 5.0),
        )
        db.add(opp)
        saved_count += 1

    elapsed = time.time() - start

    # Persist scan log
    log = ScanLogModel(
        source=",".join(spider_names),
        raw_count=len(all_items),
        unique_count=len(unique),
        merged_count=merged,
        valid_count=len(scored),
        recommended_count=saved_count,
        elapsed_seconds=elapsed,
        status="success" if not spider_errors else "partial",
        error_message="; ".join(spider_errors) if spider_errors else None,
    )
    db.add(log)
    await db.flush()

    # Send notifications for high-value opportunities
    if saved_count > 0:
        notifier = NotificationManager()
        high_value = [s for s in scored if s.get("score", 0) >= 8.5]
        if high_value:
            await notifier.send(
                title=f"🎯 发现 {len(high_value)} 个高价值机会",
                message=f"扫描完成，发现 {saved_count} 个新机会",
                priority="high",
            )

    return ScanResult(
        status="success" if not spider_errors else "partial",
        raw_count=len(all_items),
        unique_count=len(unique),
        merged_count=merged,
        valid_count=len(scored),
        recommended_count=saved_count,
        elapsed_seconds=round(elapsed, 2),
        opportunities=[],
        error_message="; ".join(spider_errors) if spider_errors else None,
    )
