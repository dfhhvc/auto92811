"""Notification delivery with multiple channel support.

Supports Pushover, email (SMTP), and generic Webhook.
"""

from __future__ import annotations

import json
import smtplib
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from typing import Any, Dict, List

import httpx

from autoincome.core.config import get_settings


class BaseNotifier(ABC):
    """Base class for notification channels."""

    @abstractmethod
    async def send(self, title: str, message: str, **kwargs: Any) -> bool:
        """Send a notification."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if this notifier is properly configured."""
        pass


class PushoverNotifier(BaseNotifier):
    """Pushover mobile push notifications."""

    API_URL = "https://api.pushover.net/1/messages.json"

    def __init__(self, app_token: str | None = None, user_key: str | None = None) -> None:
        settings = get_settings()
        self.app_token = app_token or settings.pushover_token
        self.user_key = user_key or settings.pushover_user

    def is_configured(self) -> bool:
        return bool(self.app_token and self.user_key)

    async def send(self, title: str, message: str, **kwargs: Any) -> bool:
        if not self.is_configured():
            return False

        data = {
            "token": self.app_token,
            "user": self.user_key,
            "title": title,
            "message": message,
            "priority": kwargs.get("priority", 0),
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.API_URL, data=data)
                return response.status_code == 200
        except Exception:
            return False


class EmailNotifier(BaseNotifier):
    """Email notifications via SMTP."""

    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int = 587,
        username: str | None = None,
        password: str | None = None,
        to_address: str | None = None,
    ) -> None:
        self.smtp_host = smtp_host or ""
        self.smtp_port = smtp_port
        self.username = username or ""
        self.password = password or ""
        self.to_address = to_address or ""

    def is_configured(self) -> bool:
        return all([self.smtp_host, self.username, self.password, self.to_address])

    async def send(self, title: str, message: str, **kwargs: Any) -> bool:
        if not self.is_configured():
            return False

        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = title
        msg["From"] = self.username
        msg["To"] = self.to_address

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            return True
        except Exception:
            return False


class WebhookNotifier(BaseNotifier):
    """Generic webhook notifications (WeCom/DingTalk/Feishu)."""

    def __init__(self, url: str | None = None) -> None:
        settings = get_settings()
        self.url = url or settings.webhook_url or ""

    def is_configured(self) -> bool:
        return bool(self.url)

    async def send(self, title: str, message: str, **kwargs: Any) -> bool:
        if not self.is_configured():
            return False

        platform = kwargs.get("platform", "generic")
        payload = self._format_payload(platform, title, message)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                return response.status_code == 200
        except Exception:
            return False

    def _format_payload(self, platform: str, title: str, message: str) -> Dict[str, Any]:
        if platform == "wecom":
            return {"msgtype": "text", "text": {"content": f"{title}\n{message}"}}
        if platform == "dingtalk":
            return {"msgtype": "text", "text": {"content": f"{title}\n{message}"}}
        if platform == "feishu":
            return {"msg_type": "text", "content": {"text": f"{title}\n{message}"}}
        return {"title": title, "message": message}


class NotificationManager:
    """Manages multiple notification channels."""

    def __init__(self) -> None:
        self.notifiers: List[BaseNotifier] = [
            PushoverNotifier(),
            EmailNotifier(),
            WebhookNotifier(),
        ]

    async def send(self, title: str, message: str, priority: str = "normal", **kwargs: Any) -> Dict[str, bool]:
        """Send to all configured channels."""
        results = {}
        for notifier in self.notifiers:
            if notifier.is_configured() and self._should_send(priority, notifier):
                name = type(notifier).__name__
                results[name] = await notifier.send(title, message, **kwargs)
        return results

    def _should_send(self, priority: str, notifier: BaseNotifier) -> bool:
        if priority == "urgent":
            return True
        if priority == "high":
            return not isinstance(notifier, EmailNotifier)
        if priority == "normal":
            return isinstance(notifier, (PushoverNotifier, WebhookNotifier))
        return True
