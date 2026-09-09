"""services/hacker_news_service.py — points filter, topic filter, fallback, cache write."""
import io
import json

import pytest

from services import hacker_news_service as hn


HITS = {
    "hits": [
        {"objectID": "1", "title": "GPT-5 released today", "points": 200, "url": "http://x/1", "story_text": ""},
        {"objectID": "2", "title": "Rust web framework", "points": 150, "url": "http://x/2", "story_text": ""},
        {"objectID": "3", "title": "Small AI note", "points": 5, "url": "http://x/3", "story_text": ""},
    ]
}


@pytest.fixture(autouse=True)
def _mock_boundaries(monkeypatch, tmp_path):
    monkeypatch.setattr(hn, "extract_og_image", lambda *_a, **_k: None)
    monkeypatch.setattr(hn, "_fetch_hn_item", lambda _id: {})  # no kids -> no comments
    monkeypatch.setattr(hn, "CACHE_FILE", str(tmp_path / "hn_cache.json"))

    def serve(payload):
        monkeypatch.setattr(
            hn.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(json.dumps(payload).encode())
        )

    serve(HITS)
    return serve


def test_points_threshold_and_stars_mapping():
    out = hn.fetch_hacker_news(topics=None, max_results=10)
    ids = [o["url"] for o in out]
    assert "http://x/3" not in ids  # 5 points < 40
    assert {o["url"] for o in out} == {"http://x/1", "http://x/2"}
    assert out[0]["stars"] == 200
    assert out[0]["source"] == "hacker_news"
    assert "Article Title: GPT-5 released today" in out[0]["content"]


def test_topic_filter():
    out = hn.fetch_hacker_news(topics=["gpt"], max_results=10)
    assert [o["url"] for o in out] == ["http://x/1"]


def test_fallback_to_top_3_when_filter_empties():
    out = hn.fetch_hacker_news(topics=["nonexistent-topic"], max_results=10)
    # nothing matches -> fall back to raw_hits[:3]
    assert len(out) == 3


def test_writes_cache_on_success(_mock_boundaries):
    hn.fetch_hacker_news(topics=None, max_results=10)
    with open(hn.CACHE_FILE) as f:
        cached = json.load(f)
    assert len(cached) == 2
