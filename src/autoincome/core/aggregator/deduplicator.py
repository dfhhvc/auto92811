"""Secure deduplication engine using locality-sensitive hashing.

Replaces weak MD5 with SHA-256 for fingerprinting.
No hardcoded secrets. Thread-safe.
Input size limits prevent DoS via oversized text.
"""

from __future__ import annotations

import hashlib
import threading
from typing import Dict, List, Set, Tuple


# Prevent DoS via memory exhaustion
_MAX_TEXT_LEN = 100_000  # 100KB per text field
_MAX_ITEMS = 10_000  # max items per deduplicate call


class Deduplicator:
    """Thread-safe deduplicator with SHA-256 fingerprints."""

    DOMAIN_KEYWORDS: Set[str] = frozenset({
        "赚钱", "副业", "被动收入", "自由职业", "兼职", "项目",
        "创业", "投资", "理财", "睡后收入", "斜杠",
        "AI", "自媒体", "电商", "编程", "设计", "写作",
        "翻译", "视频", "剪辑", "运营", "营销", "咨询",
        "小红书", "抖音", "B站", "知乎", "公众号", "推特",
        "闲鱼", "淘宝", "拼多多", "亚马逊", "Shopify",
        "无货源", "代发", "dropshipping", "affiliate",
        "赞助", "广告", "佣金", "会员", "订阅",
        "prompt", "midjourney", "chatgpt", "notion", "obsidian",
        "github", "sponsors", "开源", "模板", "工具",
    })

    def __init__(self, similarity_threshold: float = 0.85) -> None:
        if not isinstance(similarity_threshold, (int, float)):
            raise TypeError("threshold must be numeric")
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("threshold must be in [0.0, 1.0]")

        self.threshold = float(similarity_threshold)
        self._lock = threading.RLock()
        self._seen_hashes: Set[str] = set()

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract domain keywords from text."""
        if not isinstance(text, str) or not text:
            return []
        # Truncate oversized input to prevent CPU/memory DoS
        if len(text) > _MAX_TEXT_LEN:
            text = text[:_MAX_TEXT_LEN]
        text_lower = text.lower()
        found = [kw for kw in self.DOMAIN_KEYWORDS if kw.lower() in text_lower]
        return list(dict.fromkeys(found))

    def compute_fingerprint(self, text: str) -> str:
        """Compute SHA-256 fingerprint of extracted keywords."""
        keywords = self._extract_keywords(text)
        content = "|".join(sorted(keywords))
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:32]

    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """Compute Jaccard similarity between two texts."""
        set1 = set(self._extract_keywords(text1))
        set2 = set(self._extract_keywords(text2))
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def is_duplicate(
        self, new_item: Dict[str, Any], existing_items: List[Dict[str, Any]]
    ) -> Tuple[bool, int]:
        """Check if new_item duplicates any existing item."""
        title = str(new_item.get("title", ""))[:512]
        desc = str(new_item.get("description", ""))[:4096]
        new_text = f"{title} {desc}"

        for idx, existing in enumerate(existing_items):
            etitle = str(existing.get("title", ""))[:512]
            edesc = str(existing.get("description", ""))[:4096]
            existing_text = f"{etitle} {edesc}"
            similarity = self.jaccard_similarity(new_text, existing_text)
            if similarity >= self.threshold:
                return True, idx
        return False, -1

    def deduplicate(
        self, items: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Deduplicate a list of items. Thread-safe."""
        if not items:
            return [], 0
        if len(items) > _MAX_ITEMS:
            items = items[:_MAX_ITEMS]

        with self._lock:
            unique_items: List[Dict[str, Any]] = []
            merged_count = 0

            for item in items:
                is_dup, dup_idx = self.is_duplicate(item, unique_items)
                if is_dup and dup_idx >= 0:
                    existing = unique_items[dup_idx]
                    existing["sources"] = existing.get("sources", []) + [
                        str(item.get("source", ""))[:128]
                    ]
                    existing["merge_count"] = existing.get("merge_count", 1) + 1
                    if len(str(item.get("description", ""))) > len(
                        str(existing.get("description", ""))
                    ):
                        existing["description"] = str(item.get("description", ""))[:4096]
                    merged_count += 1
                else:
                    item["sources"] = [str(item.get("source", ""))[:128]]
                    item["merge_count"] = 1
                    unique_items.append(item)

            return unique_items, merged_count

    def get_stats(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Return deduplication statistics."""
        total_merged = sum(
            max(0, item.get("merge_count", 1) - 1) for item in items
        )
        return {
            "unique_count": len(items),
            "total_sources": sum(item.get("merge_count", 1) for item in items),
            "merged_count": total_merged,
        }
