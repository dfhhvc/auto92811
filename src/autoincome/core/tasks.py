"""Celery asynchronous task queue.

Background tasks:
- Spider execution (non-blocking)
- Notification delivery (async)
- Data cleanup (scheduled)
- Report generation (heavy computation)
"""

from __future__ import annotations

from celery import Celery
from celery.signals import task_failure, task_postrun, task_prerun

from autoincome.core.config import get_settings
from autoincome.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

# ── Celery App ──────────────────────────────────────────────────

celery_app = Celery(
    "autoincome",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "autoincome.core.tasks.spiders",
        "autoincome.core.tasks.notifications",
        "autoincome.core.tasks.maintenance",
    ],
)

celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=300,      # 5 min hard limit
    task_soft_time_limit=240,  # 4 min soft limit
    worker_prefetch_multiplier=1,  # Fair task distribution
    worker_max_tasks_per_child=1000,  # Restart workers periodically

    # Result backend
    result_expires=3600,  # 1 hour
    result_extended=True,

    # RedBeat scheduler (for periodic tasks)
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_redis_url=settings.celery_broker_url,
    redbeat_lock_timeout=60,
)

# ── Task Lifecycle Hooks ────────────────────────────────────────

@task_prerun.connect
def task_prerun_handler(task_id: str, task: Any, args: Any, kwargs: Any) -> None:
    """Log task start."""
    logger.info(
        "task_started",
        task_name=task.name,
        task_id=task_id,
    )


@task_postrun.connect
def task_postrun_handler(
    task_id: str,
    task: Any,
    args: Any,
    kwargs: Any,
    retval: Any,
    state: str,
) -> None:
    """Log task completion."""
    logger.info(
        "task_completed",
        task_name=task.name,
        task_id=task_id,
        state=state,
    )


@task_failure.connect
def task_failure_handler(
    task_id: str,
    exception: Exception,
    args: Any,
    kwargs: Any,
    traceback: Any,
    einfo: Any,
) -> None:
    """Log task failure."""
    logger.error(
        "task_failed",
        task_id=task_id,
        exception=str(exception),
        traceback=str(traceback),
    )
