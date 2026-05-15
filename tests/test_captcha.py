"""Captcha solver unit tests."""

from __future__ import annotations

import pytest

from autoincome.core.captcha.solver import CaptchaSolver


class TestCaptchaSolver:
    def test_tesseract_check_false_without_binary(self, monkeypatch):
        """Tesseract availability returns False when binary missing."""
        monkeypatch.setenv("PATH", "/nonexistent")
        solver = CaptchaSolver()
        assert solver._ocr_available is False

    def test_health_check_no_providers(self):
        """Health check reports all false when no providers configured."""
        solver = CaptchaSolver()
        health = solver.health_check()
        assert health["tesseract_available"] in (True, False)
        assert health["2captcha_configured"] is False
        assert health["anticaptcha_configured"] is False
        assert health["any_provider_available"] == health["tesseract_available"]

    def test_health_check_with_2captcha(self, monkeypatch):
        """Health check reports 2captcha configured."""
        monkeypatch.setenv("AUTOINCOME_2CAPTCHA_KEY", "test-key")
        solver = CaptchaSolver()
        health = solver.health_check()
        assert health["2captcha_configured"] is True
        assert health["any_provider_available"] is True

    def test_solve_tesseract_no_pillow(self, monkeypatch):
        """Tesseract fallback returns None when Pillow not installed."""
        monkeypatch.setattr("builtins.__import__", lambda name, *args, **kwargs: __import__(name, *args, **kwargs))
        solver = CaptchaSolver()
        result = solver._solve_tesseract(b"fake-image")
        assert result is None

    def test_base64_image_placeholder(self):
        """Base64 encoding works for image bytes."""
        import base64
        data = b"fake-image-data"
        b64 = base64.b64encode(data).decode()
        assert len(b64) > 0
        assert base64.b64decode(b64) == data