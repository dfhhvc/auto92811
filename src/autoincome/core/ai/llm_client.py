"""Unified LLM client with multi-provider support.

Supports OpenAI-compatible APIs, Moonshot (Kimi), and local Ollama.
Auto-falls back through the provider chain if one fails.
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)

_DEFAULT_TIMEOUT = 60.0
_MAX_RETRIES = 2


@dataclass(frozen=True)
class LLMResponse:
    """Structured LLM response."""

    text: str
    model: str
    usage: dict[str, int] | None = None
    raw: dict[str, Any] | None = None


class LLMClient:
    """Multi-provider LLM client with fallback chain.

    Provider priority:
    1. Moonshot (Kimi) — if AUTOINCOME_MOONSHOT_API_KEY is set
    2. OpenRouter — if AUTOINCOME_OPENROUTER_API_KEY is set
    3. OpenAI — if OPENAI_API_KEY is set
    4. Local Ollama — if available on localhost:11434
    """

    def __init__(self) -> None:
        self._providers: list[dict[str, Any]] = []
        self._init_providers()

    def _init_providers(self) -> None:
        """Build provider chain from environment."""
        # Moonshot / Kimi
        moonshot_key = os.getenv("AUTOINCOME_MOONSHOT_API_KEY") or os.getenv("MOONSHOT_API_KEY")
        if moonshot_key:
            self._providers.append({
                "name": "moonshot",
                "base_url": "https://api.moonshot.cn/v1",
                "api_key": moonshot_key,
                "model": os.getenv("AUTOINCOME_MOONSHOT_MODEL", "moonshot-v1-8k"),
                "headers": {"Authorization": f"Bearer {moonshot_key}"},
            })
            logger.info("llm_provider_registered", provider="moonshot")

        # OpenRouter
        openrouter_key = os.getenv("AUTOINCOME_OPENROUTER_API_KEY")
        if openrouter_key:
            self._providers.append({
                "name": "openrouter",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": openrouter_key,
                "model": os.getenv("AUTOINCOME_OPENROUTER_MODEL", "moonshot/kimi-k2.5"),
                "headers": {
                    "Authorization": f"Bearer {openrouter_key}",
                    "HTTP-Referer": "https://github.com/dfhhvc/auto92811",
                    "X-Title": "AutoIncome",
                },
            })
            logger.info("llm_provider_registered", provider="openrouter")

        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self._providers.append({
                "name": "openai",
                "base_url": "https://api.openai.com/v1",
                "api_key": openai_key,
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "headers": {"Authorization": f"Bearer {openai_key}"},
            })
            logger.info("llm_provider_registered", provider="openai")

        # Local Ollama (discovered at runtime)
        self._providers.append({
            "name": "ollama",
            "base_url": os.getenv("OLLAMA_HOST", "http://localhost:11434/v1"),
            "api_key": "ollama",
            "model": os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
            "headers": {},
            "optional": True,
        })

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send chat completion request with automatic fallback.

        Args:
            messages: OpenAI-format message list.
            temperature: Sampling temperature.
            max_tokens: Max output tokens.
            json_mode: Force JSON output if supported.

        Returns:
            LLMResponse with generated text.

        Raises:
            RuntimeError: If all providers fail.
        """
        last_error: Exception | None = None

        for provider in self._providers:
            try:
                result = await self._try_provider(
                    provider, messages, temperature, max_tokens, json_mode
                )
                logger.info(
                    "llm_request_success",
                    provider=provider["name"],
                    model=result.model,
                )
                return result
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "llm_provider_failed",
                    provider=provider["name"],
                    error=str(exc),
                )
                continue

        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    async def _try_provider(
        self,
        provider: dict[str, Any],
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        json_mode: bool,
    ) -> LLMResponse:
        """Attempt a single provider request."""
        payload: dict[str, Any] = {
            "model": provider["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(
            timeout=_DEFAULT_TIMEOUT,
            headers=provider["headers"],
        ) as client:
            response = await client.post(
                f"{provider['base_url']}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            content = choice["message"]["content"]

            return LLMResponse(
                text=content,
                model=data.get("model", provider["model"]),
                usage=data.get("usage"),
                raw=data,
            )

    async def analyze_text(
        self,
        text: str,
        system_prompt: str,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Convenience wrapper for single-turn analysis."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
        return await self.chat(messages, json_mode=json_mode)

    def health_check(self) -> dict[str, bool]:
        """Check which providers are configured."""
        return {
            p["name"]: not p.get("optional", False)
            for p in self._providers
        }


# Global singleton
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client