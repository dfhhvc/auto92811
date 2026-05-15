"""Deduplicator unit tests."""

from __future__ import annotations

import pytest

from autoincome.core.aggregator.deduplicator import Deduplicator


class TestDeduplicator:
    def test_exact_duplicate(self):
        d = Deduplicator(similarity_threshold=0.85)
        items = [
            {"title": "AI写作赚钱", "description": "用ChatGPT写文章赚钱", "source": "知乎"},
            {"title": "AI写作赚钱", "description": "用ChatGPT写文章赚钱", "source": "V2EX"},
        ]
        unique, merged = d.deduplicate(items)
        assert len(unique) == 1
        assert merged == 1

    def test_no_duplicate(self):
        d = Deduplicator(similarity_threshold=0.85)
        items = [
            {"title": "AI写作", "description": "用ChatGPT写文章", "source": "知乎"},
            {"title": "闲鱼电商", "description": "在闲鱼卖东西", "source": "V2EX"},
        ]
        unique, merged = d.deduplicate(items)
        assert len(unique) == 2
        assert merged == 0

    def test_invalid_threshold_high(self):
        with pytest.raises(ValueError):
            Deduplicator(similarity_threshold=1.5)

    def test_invalid_threshold_low(self):
        with pytest.raises(ValueError):
            Deduplicator(similarity_threshold=-0.1)

    def test_empty_list(self):
        d = Deduplicator()
        unique, merged = d.deduplicate([])
        assert unique == []
        assert merged == 0

    def test_thread_safety(self):
        import threading

        d = Deduplicator()
        results = []

        def worker():
            items = [{"title": f"t{i}", "description": f"desc{i}", "source": "s"} for i in range(10)]
            u, m = d.deduplicate(items)
            results.append((len(u), m))

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == 5
