"""Captcha solver with multi-provider support and graceful degradation.

Providers (in priority order):
1. 2captcha.com — cloud human-solving service
2. Anti-Captcha — alternative cloud service
3. Local Tesseract OCR — for simple text captchas
4. Manual queue — log unsolvable captchas for later review
"""

from __future__ import annotations

import base64
import io
import os
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)

_CAPTCHA_TIMEOUT = 120.0


class CaptchaSolver:
    """Unified captcha solver with provider fallback."""

    def __init__(self) -> None:
        self._twocaptcha_key = os.getenv("AUTOINCOME_2CAPTCHA_KEY")
        self._anticaptcha_key = os.getenv("AUTOINCOME_ANTICAPTCHA_KEY")
        self._ocr_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is available."""
        try:
            import subprocess
            subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except Exception:
            return False

    async def solve_image(self, image_bytes: bytes) -> str | None:
        """Solve an image captcha.

        Args:
            image_bytes: Raw image data (PNG/JPEG).

        Returns:
            Solved text, or None if all providers failed.
        """
        # Try 2captcha first
        if self._twocaptcha_key:
            try:
                result = await self._solve_2captcha(image_bytes)
                if result:
                    return result
            except Exception as exc:
                logger.warning("2captcha_failed", error=str(exc))

        # Try Anti-Captcha
        if self._anticaptcha_key:
            try:
                result = await self._solve_anticaptcha(image_bytes)
                if result:
                    return result
            except Exception as exc:
                logger.warning("anticaptcha_failed", error=str(exc))

        # Try local OCR
        if self._ocr_available:
            try:
                result = self._solve_tesseract(image_bytes)
                if result:
                    return result
            except Exception as exc:
                logger.warning("tesseract_failed", error=str(exc))

        logger.error("captcha_unsolvable", size=len(image_bytes))
        return None

    async def solve_recaptcha_v2(
        self, site_key: str, page_url: str
    ) -> str | None:
        """Solve Google reCAPTCHA v2.

        Args:
            site_key: The data-sitekey attribute.
            page_url: The URL of the page containing the captcha.

        Returns:
            The g-recaptcha-response token.
        """
        if self._twocaptcha_key:
            try:
                return await self._solve_recaptcha_2captcha(site_key, page_url)
            except Exception as exc:
                logger.warning("recaptcha_2captcha_failed", error=str(exc))

        if self._anticaptcha_key:
            try:
                return await self._solve_recaptcha_anticaptcha(site_key, page_url)
            except Exception as exc:
                logger.warning("recaptcha_anticaptcha_failed", error=str(exc))

        logger.error("recaptcha_unsolvable", site_key=site_key)
        return None

    # ── 2captcha implementation ──────────────────────────────────

    async def _solve_2captcha(self, image_bytes: bytes) -> str | None:
        """Submit image to 2captcha and poll for result."""
        b64 = base64.b64encode(image_bytes).decode()

        async with httpx.AsyncClient(timeout=_CAPTCHA_TIMEOUT) as client:
            # Submit
            submit_url = "http://2captcha.com/in.php"
            submit_data = {
                "key": self._twocaptcha_key,
                "method": "base64",
                "body": b64,
                "json": 1,
            }
            resp = await client.post(submit_url, data=submit_data)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != 1:
                raise RuntimeError(f"2captcha submit error: {data}")

            captcha_id = data["request"]
            logger.info("2captcha_submitted", id=captcha_id)

            # Poll for result
            result_url = "http://2captcha.com/res.php"
            for attempt in range(30):
                await asyncio.sleep(5)
                poll = await client.get(
                    result_url,
                    params={
                        "key": self._twocaptcha_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1,
                    },
                )
                poll_data = poll.json()
                if poll_data.get("status") == 1:
                    return poll_data["request"]
                if poll_data.get("request") != "CAPCHA_NOT_READY":
                    raise RuntimeError(f"2captcha error: {poll_data}")

            raise TimeoutError("2captcha polling timeout")

    async def _solve_recaptcha_2captcha(
        self, site_key: str, page_url: str
    ) -> str | None:
        """Submit reCAPTCHA v2 to 2captcha."""
        async with httpx.AsyncClient(timeout=_CAPTCHA_TIMEOUT) as client:
            submit_url = "http://2captcha.com/in.php"
            submit_data = {
                "key": self._twocaptcha_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
                "json": 1,
            }
            resp = await client.post(submit_url, data=submit_data)
            data = resp.json()

            if data.get("status") != 1:
                raise RuntimeError(f"2captcha recaptcha submit error: {data}")

            captcha_id = data["request"]
            result_url = "http://2captcha.com/res.php"
            for _ in range(30):
                await asyncio.sleep(5)
                poll = await client.get(
                    result_url,
                    params={
                        "key": self._twocaptcha_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1,
                    },
                )
                poll_data = poll.json()
                if poll_data.get("status") == 1:
                    return poll_data["request"]
                if poll_data.get("request") != "CAPCHA_NOT_READY":
                    raise RuntimeError(f"2captcha recaptcha error: {poll_data}")

            raise TimeoutError("2captcha recaptcha polling timeout")

    # ── Anti-Captcha implementation ──────────────────────────────

    async def _solve_anticaptcha(self, image_bytes: bytes) -> str | None:
        """Submit image to Anti-Captcha."""
        b64 = base64.b64encode(image_bytes).decode()

        async with httpx.AsyncClient(timeout=_CAPTCHA_TIMEOUT) as client:
            create_url = "https://api.anti-captcha.com/createTask"
            create_payload = {
                "clientKey": self._anticaptcha_key,
                "task": {
                    "type": "ImageToTextTask",
                    "body": b64,
                },
            }
            resp = await client.post(create_url, json=create_payload)
            data = resp.json()

            if data.get("errorId", 0) != 0:
                raise RuntimeError(f"Anti-Captcha error: {data}")

            task_id = data["taskId"]
            logger.info("anticaptcha_submitted", id=task_id)

            result_url = "https://api.anti-captcha.com/getTaskResult"
            for _ in range(30):
                await asyncio.sleep(5)
                poll = await client.post(
                    result_url,
                    json={"clientKey": self._anticaptcha_key, "taskId": task_id},
                )
                poll_data = poll.json()
                if poll_data.get("status") == "ready":
                    return poll_data["solution"]["text"]

            raise TimeoutError("Anti-Captcha polling timeout")

    async def _solve_recaptcha_anticaptcha(
        self, site_key: str, page_url: str
    ) -> str | None:
        """Submit reCAPTCHA v2 to Anti-Captcha."""
        async with httpx.AsyncClient(timeout=_CAPTCHA_TIMEOUT) as client:
            create_url = "https://api.anti-captcha.com/createTask"
            create_payload = {
                "clientKey": self._anticaptcha_key,
                "task": {
                    "type": "NoCaptchaTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key,
                },
            }
            resp = await client.post(create_url, json=create_payload)
            data = resp.json()

            if data.get("errorId", 0) != 0:
                raise RuntimeError(f"Anti-Captcha recaptcha error: {data}")

            task_id = data["taskId"]
            result_url = "https://api.anti-captcha.com/getTaskResult"
            for _ in range(30):
                await asyncio.sleep(5)
                poll = await client.post(
                    result_url,
                    json={"clientKey": self._anticaptcha_key, "taskId": task_id},
                )
                poll_data = poll.json()
                if poll_data.get("status") == "ready":
                    return poll_data["solution"]["gRecaptchaResponse"]

            raise TimeoutError("Anti-Captcha recaptcha polling timeout")

    # ── Tesseract OCR fallback ───────────────────────────────────

    def _solve_tesseract(self, image_bytes: bytes) -> str | None:
        """Solve simple text captcha with Tesseract OCR."""
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            logger.warning("tesseract_not_installed")
            return None

        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang="eng+chi_sim")
        text = text.strip().replace(" ", "").replace("\n", "")
        if len(text) >= 3:
            return text
        return None

    def health_check(self) -> dict[str, Any]:
        """Report solver health status."""
        return {
            "tesseract_available": self._ocr_available,
            "2captcha_configured": bool(self._twocaptcha_key),
            "anticaptcha_configured": bool(self._anticaptcha_key),
            "any_provider_available": bool(
                self._twocaptcha_key or self._anticaptcha_key or self._ocr_available
            ),
        }


# Global singleton
_captcha_solver: CaptchaSolver | None = None


def get_captcha_solver() -> CaptchaSolver:
    """Get or create global captcha solver."""
    global _captcha_solver
    if _captcha_solver is None:
        _captcha_solver = CaptchaSolver()
    return _captcha_solver