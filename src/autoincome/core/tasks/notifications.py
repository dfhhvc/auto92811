"""Celery tasks for notification delivery.

Async delivery to multiple channels:
- Pushover push notifications
- Email (SMTP)
- Webhook (generic HTTP POST)
"""

from __future__ import annotations

from typing import Any

from autoincome.core.config import get_settings
from autoincome.core.logging_config import get_logger
from autoincome.core.metrics import notifications_sent_total
from autoincome.core.notifier.push import (
    EmailNotifier,
    PushoverNotifier,
    WebhookNotifier,
)
from autoincome.core.tasks import celery_app

logger = get_logger(__name__)
settings = get_settings()


@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=30,
    autoretry_for=(ConnectionError, TimeoutError),
)
def send_notification(
    self,
    channel: str,
    title: str,
    message: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Send notification via specified channel.

    Args:
        channel: "pushover", "email", or "webhook"
        title: Notification title
        message: Notification body
        **kwargs: Channel-specific options

    Returns:
        Delivery result with status.
    """
    notifier = _get_notifier(channel)
    if not notifier or not notifier.is_configured():
        logger.warning("notification_skipped", channel=channel, reason="not_configured")
        return {"channel": channel, "status": "skipped", "reason": "not_configured"}

    try:
        success = notifier.send(title, message, **kwargs)
        status = "delivered" if success else "failed"
        notifications_sent_total.labels(channel=channel, status=status).inc()

        logger.info("notification_sent", channel=channel, status=status)
        return {"channel": channel, "status": status}

    except Exception as exc:
        notifications_sent_total.labels(channel=channel, status="error").inc()
        logger.error("notification_failed", channel=channel, error=str(exc))
        raise self.retry(exc=exc)


def _get_notifier(channel: str) -> Any | None:
    """Get notifier instance by channel name."""
    notifiers = {
        "pushover": PushoverNotifier(),
        "email": EmailNotifier(),
        "webhook": WebhookNotifier(),
    }
    return notifiers.get(channel)


@celery_app.task
def broadcast_notification(title: str, message: str, **kwargs: Any) -> dict[str, Any]:
    """Send notification to all configured channels."""
    results = {}

    for channel in ["pushover", "email", "webhook"]:
        result = send_notification.delay(channel, title, message, **kwargs)
        results[channel] = {"task_id": result.id}

    return {"channels": results, "status": "queued"}
