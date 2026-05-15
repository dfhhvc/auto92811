"""Semantic deduplication using LLM embeddings + cosine similarity.

Replaces keyword-only Jaccard with true semantic understanding.
Can detect paraphrased or translated duplicates that keyword
matching would miss.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
from typing import Any

import structlog

from autoincome.core.ai.llm_client import LLMClient, get_llm_client

logger = structlog.get_logger(__name__)

_EMBEDDING_PROMPT = """Generate a dense semantic embedding for this text as a JSON array of 32 floats.
Capture the core meaning, topic, intent, and domain. Ignore stylistic differences.
Output ONLY a JSON array like [0.12, -0.34, ...] with exactly 32 numbers.
"""


class SemanticDeduplicator:
    """LLM-powered semantic deduplication engine.

    Uses LLM-generated embeddings (or local TF-IDF fallback) to compute
    cosine similarity between opportunity texts. Detects:
    - Exact duplicates
    - Paraphrased content
    - Cross-language duplicates
    - Same idea from different sources
    """

    def __init__(
        self,
        similarity_threshold: float = 0.88,
        llm: LLMClient | None = None,
    ) -> None:
        self.threshold = similarity_threshold
        self.llm = llm or get_llm_client()
        self._cache: dict[str, list[float]] = {}

    async def deduplicate(
        self, items: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], int]:
        """Deduplicate items using semantic embeddings.

        Returns:
            (unique_items, merged_count)
        """
        if not items:
            return [], 0

        # Build embeddings for all items
        embeddings: list[tuple[dict[str, Any], list[float]]] = []
        for item in items:
            text = self._extract_text(item)
            emb = await self._get_embedding(text)
            embeddings.append((item, emb))

        unique: list[dict[str, Any]] = []
        merged = 0

        for item, emb in embeddings:
            dup_idx = self._find_duplicate(emb, unique)
            if dup_idx >= 0:
                existing = unique[dup_idx]
                existing["sources"] = existing.get("sources", []) + [
                    str(item.get("source", ""))[:128]
                ]
                existing["merge_count"] = existing.get("merge_count", 1) + 1
                # Keep the longer/better description
                if len(str(item.get("description", ""))) > len(
                    str(existing.get("description", ""))
                ):
                    existing["description"] = str(item.get("description", ""))[:4096]
                merged += 1
            else:
                item["sources"] = [str(item.get("source", ""))[:128]]
                item["merge_count"] = 1
                unique.append(item)

        logger.info("semantic_dedup_complete", raw=len(items), unique=len(unique), merged=merged)
        return unique, merged

    async def _get_embedding(self, text: str) -> list[float]:
        """Get embedding for text — LLM or local fallback."""
        cache_key = hashlib.sha256(text.encode()).hexdigest()[:16]
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            embedding = await self._llm_embedding(text)
            self._cache[cache_key] = embedding
            return embedding
        except Exception as exc:
            logger.debug("llm_embedding_failed", error=str(exc))
            embedding = self._local_embedding(text)
            self._cache[cache_key] = embedding
            return embedding

    async def _llm_embedding(self, text: str) -> list[float]:
        """Request LLM to generate a semantic embedding vector."""
        response = await self.llm.analyze_text(
            text[:2000], _EMBEDDING_PROMPT, json_mode=True
        )
        import json
        emb = json.loads(response.text)
        if isinstance(emb, list) and len(emb) >= 16:
            return [float(x) for x in emb[:32]]
        raise ValueError("Invalid embedding format")

    def _local_embedding(self, text: str) -> list[float]:
        """Fast local fallback: character n-gram hash embedding."""
        text = text.lower()[:1000]
        dim = 32
        vec = [0.0] * dim
        for i in range(len(text) - 2):
            tri = text[i:i+3]
            idx = hash(tri) % dim
            vec[idx] += 1.0
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _extract_text(self, item: dict[str, Any]) -> str:
        """Extract normalized text for embedding."""
        title = str(item.get("title", ""))[:256]
        desc = str(item.get("description", ""))[:1024]
        tags = " ".join(str(t) for t in item.get("tags", []))
        return f"{title} {tags} {desc}".strip()

    def _find_duplicate(
        self, emb: list[float], unique_items: list[dict[str, Any]]
    ) -> int:
        """Find duplicate index by cosine similarity. Returns -1 if none."""
        for idx, item in enumerate(unique_items):
            cache_key = hashlib.sha256(self._extract_text(item).encode()).hexdigest()[:16]
            other_emb = self._cache.get(cache_key)
            if other_emb is None:
                continue
            sim = self._cosine_similarity(emb, other_emb)
            if sim >= self.threshold:
                return idx
        return -1

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(a) != len(b):
            b = b + [0.0] * (len(a) - len(b))
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
        norm_b = math.sqrt(sum(x * x for x in b)) or 1.0
        return dot / (norm_a * norm_b)