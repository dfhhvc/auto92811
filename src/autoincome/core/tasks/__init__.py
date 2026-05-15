"""Celery tasks package."""

from __future__ import annotations

from autoincome.core.tasks.spiders import run_spider, scan_all_spiders
from autoincome.core.tasks.notifications import send_notification, broadcast_notification
from autoincome.core.tasks.maintenance import (
    cleanup_expired_tokens,
    cleanup_old_scan_logs,
    refresh_cache_stats,
    database_maintenance,
)

__all__ = [
    "run_spider",
    "scan_all_spiders",
    "send_notification",
    "broadcast_notification",
    "cleanup_expired_tokens",
    "cleanup_old_scan_logs",
    "refresh_cache_stats",
    "database_maintenance",
]