"""services/tavily_service.py — result parsing, raw_content preference, image fallback."""
import pytest

from services import tavily_service


class _FakeClient:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def __call__(self, api_key=None):  # TavilyClient(api_key=...)
        return self

    def search(self, **kwargs):
        self.calls.append(kwargs)
        return self._response


@pytest.fixture
def fake_tavily(monkeypatch):
    def _install(response):
        client = _FakeClient(response)
        monkeypatch.setattr(tavily_service, "TavilyClient", client)
        return client

    return _install


def test_prefers_long_raw_content_else_content(fake_tavily):
    fake_tavily(
        {
            "results": [
                {"title": "Long", "url": "u1", "raw_content": "R" * 600, "content": "short fallback"},
                {"title": "Short raw", "url": "u2", "raw_content": "tiny", "content": "the real content"},
            ],
            "images": ["http://img/0"],
        }
    )

    out = tavily_service.fetch_ai_news(queries=["q"], max_results=2)

    assert out[0]["content"] == "R" * 600  # raw_content used (>=500)
    assert out[1]["content"] == "the real content"  # raw too short -> content
    assert out[0]["source"] == "tavily"


def test_image_fallback_to_picsum_when_images_short(fake_tavily):
    fake_tavily({"results": [{"title": "A", "url": "u", "content": "c"}], "images": []})

    out = tavily_service.fetch_ai_news(queries=["q"], max_results=1)

    assert out[0]["image_url"].startswith("https://picsum.photos/seed/")


def test_iterates_all_queries(fake_tavily):
    client = fake_tavily({"results": [], "images": []})
    tavily_service.fetch_ai_news(queries=["a", "b", "c"], max_results=1)
    assert [c["query"] for c in client.calls] == ["a", "b", "c"]


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(ValueError):
        tavily_service.fetch_ai_news(queries=["q"])
