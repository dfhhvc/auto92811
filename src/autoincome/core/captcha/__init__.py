"""Captcha solving adapters for spider automation.

Supports:
- 2captcha / Anti-Captcha (cloud services)
- Local OCR fallback (Tesseract)
- Manual queue for unsolvable cases
"""

from __future__ import annotations

from autoincome.core.captcha.solver import CaptchaSolver, get_captcha_solver

__all__ = ["CaptchaSolver", "get_captcha_solver"]