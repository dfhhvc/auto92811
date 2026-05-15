"""Celery tasks for spider execution.

Runs spiders asynchronously in background workers:
- Non-blocking API responses
- Retry on transient failures
- Result caching via Redis
- Metrics collection
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from autoincome.core.cache import cache
from autoincome.core.config import get_settings
from autoincome.core.logging_config import get_logger
from autoincome.core.metrics import record_cache_hit, record_cache_miss, record_spider_run
from autoincome.core.tasks import celery_app

logger = get_logger(__name__)
settings = get_settings()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,
)
def run_spider(self, spider_name: str, **kwargs: Any) -> dict[str, Any]:
    """Execute a spider asynchronously.

    Args:
        spider_name: Name of the spider to run.
        **kwargs: Additional spider parameters.

    Returns:
        Spider execution results with metadata.
    """
    import asyncio

    return asyncio.run(_run_spider_async(spider_name, kwargs))


async def _run_spider_async(spider_name: str, params: dict) -> dict[str, Any]:
    """Async implementation of spider execution."""
    start_time = time.time()

    # Check cache first
    cached = await cache.get_spider_result(spider_name, params)
    if cached:
        record_cache_hit("spider")
        logger.info("spider_cache_hit", spider=spider_name)
        return {
            "spider": spider_name,
            "results": cached,
            "cached": True,
            "count": len(cached),
        }

    record_cache_miss("spider")

    # Import and run spider dynamically
    try:
        from autoincome.core.spiders import registry

        spider_class = registry.get(spider_name)
        if not spider_class:
            raise ValueError(f"Unknown spider: {spider_name}")

        spider = spider_class()
        results = await spider.fetch(**params)

        # Cache results
        await cache.set_spider_result(spider_name, results, params)

        duration = time.time() - start_time
        record_spider_run(spider_name, "success", duration, len(results))

        logger.info(
            "spider_completed",
            spider=spider_name,
            results=len(results),
            duration=duration,
        )

        return {
            "spider": spider_name,
            "results": results,
            "cached": False,
            "count": len(results),
            "duration": round(duration, 2),
        }

    except Exception as exc:
        duration = time.time() - start_time
        record_spider_run(spider_name, "error", duration, 0)
        logger.error(
            "spider_failed",
            spider=spider_name,
            error=str(exc),
            duration=duration,
        )
        raise


@celery_app.task
def scan_all_spiders() -> dict[str, Any]:
    """Run all enabled spiders sequentially."""
    import asyncio

    return asyncio.run(_scan_all_async())


async def _scan_all_async() -> dict[str, Any]:
    """Async implementation of full scan."""
    from autoincome.core.spiders import registry

    results = {}
    total = 0

    for spider_name in registry.list_spiders():
        try:
            result = await _run_spider_async(spider_name, {})
            results[spider_name] = result
            total += result.get("count", 0)
        except Exception as exc:
            results[spider_name] = {"error": str(exc)}

    return {
        "spiders": results,
        "total_results": total,
        "timestamp": time.time(),
    }
