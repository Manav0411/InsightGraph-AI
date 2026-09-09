"""agents/composer.py — markdown assembly (LLM intro skipped by unsetting GROQ_API_KEY)."""
import pytest

from agents.composer import compose_newsletter


@pytest.fixture(autouse=True)
def _no_groq(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)


def _analyzed(make_article, **over):
    base = dict(
        summary="A grounded summary of the story.",
        why_it_matters="Because it matters to the ecosystem.",
        tags=["Tag"],
        details=["d1", "d2"],
        trend_score=3.0,
    )
    base.update(over)
    return make_article(**base)


def test_sections_present_per_source(make_state, make_article):
    arts = [
        _analyzed(make_article, title="News one", source="tavily"),
        _analyzed(make_article, title="Paper one", source="arxiv"),
        _analyzed(make_article, title="HN one", source="hacker_news"),
        _analyzed(make_article, title="RSS one", source="rss"),
    ]
    out = compose_newsletter(make_state(articles=arts))

    md = out.final_newsletter
    assert md.startswith("# InsightGraph Digest")
    assert "## Top Stories" in md
    assert "## Cutting-Edge Research (ArXiv)" in md
    assert "## Community Pulse (Hacker News)" in md
    assert "## Official Lab Announcements" in md
    assert "News one" in md and "Paper one" in md


def test_recommended_section_only_when_boosted(make_state, make_article):
    plain = _analyzed(make_article, title="Plain story", source="tavily", personalization_boost=0.0)
    boosted = _analyzed(make_article, title="Boosted story", source="tavily", personalization_boost=3.0)

    no_rec = compose_newsletter(make_state(articles=[plain]))
    assert "## Recommended For You" not in no_rec.final_newsletter

    with_rec = compose_newsletter(make_state(articles=[plain, boosted]))
    assert "## Recommended For You" in with_rec.final_newsletter
    assert "Boosted story" in with_rec.final_newsletter.split("## Top Stories")[0]


def test_timing_recorded(make_state, make_article):
    out = compose_newsletter(make_state(articles=[_analyzed(make_article)]))
    assert "composer" in out.metadata.agent_timings
