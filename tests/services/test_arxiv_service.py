"""services/arxiv_service.py — query build (regression: single-encoded) + parsing."""
import io
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from services import arxiv_service

FIXTURE = (Path(__file__).parent.parent / "fixtures" / "arxiv_response.xml").read_bytes()


@pytest.fixture
def capture_url(monkeypatch):
    seen = {}

    def fake_urlopen(req, timeout=None):
        seen["url"] = req.full_url if hasattr(req, "full_url") else req.get_full_url()
        return io.BytesIO(FIXTURE)

    monkeypatch.setattr(arxiv_service.urllib.request, "urlopen", fake_urlopen)
    return seen


def test_query_is_category_based_and_single_encoded(capture_url):
    arxiv_service.fetch_arxiv_papers(topics=["Large Language Models (LLMs)"], max_results=5)

    qs = parse_qs(urlparse(capture_url["url"]).query)
    # regression: the verbose topic must NOT leak in, and no double-encoding (%2520)
    assert qs["search_query"][0] == "cat:cs.AI OR cat:cs.CL OR cat:cs.LG"
    assert "%25" not in capture_url["url"]
    assert qs["max_results"][0] == "5"
    assert qs["sortBy"][0] == "submittedDate"


def test_parses_entries(capture_url):
    out = arxiv_service.fetch_arxiv_papers(max_results=5)

    assert len(out) == 2
    first = out[0]
    assert first["title"] == "A Study of Large Language Models"  # newlines collapsed
    assert first["url"] == "http://arxiv.org/pdf/2501.00001v1"
    assert first["content"].startswith("Abstract: We investigate scaling")
    assert first["source"] == "arxiv"
    assert first["image_url"] is None
    # entry without a pdf <link> falls back to the <id>
    assert out[1]["url"] == "http://arxiv.org/abs/2501.00002v1"


def test_empty_body_returns_empty(monkeypatch):
    monkeypatch.setattr(
        arxiv_service.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(b"<feed xmlns='http://www.w3.org/2005/Atom'></feed>")
    )
    assert arxiv_service.fetch_arxiv_papers() == []
