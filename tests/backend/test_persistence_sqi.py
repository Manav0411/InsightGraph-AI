"""backend/services/persistence_service.py::save_briefing — SQI math + metadata extraction.

Uses a MagicMock session: save_briefing only calls .add / .flush / .commit / .refresh.
"""
from unittest.mock import MagicMock

import pytest

from backend.schemas.responses import ArticleResponse, NewsletterResponse, TrustMetrics
from backend.services import persistence_service


@pytest.fixture(autouse=True)
def _patch_deps(monkeypatch):
    monkeypatch.setattr(persistence_service, "create_or_get_user", lambda *a, **k: MagicMock())
    # store_briefing is imported lazily inside save_briefing; patch the module singleton
    import backend.services.vector_store as vs

    monkeypatch.setattr(vs.memory_manager, "store_briefing", lambda *a, **k: None)


def _article(**over):
    base = dict(
        title="A", url="u", image_url=None, summary="s", details=["d1", "d2"], why_it_matters="w",
        source="tavily", tags=["Models"], trend_score=4.0, personalization_boost=0.0, stars=None,
        recommendation_reasons=[], grounding_verified=True,
    )
    base.update(over)
    return ArticleResponse(**base)


def _response(articles, grounding=100.0, validation=100.0):
    return NewsletterResponse(
        message="ok",
        newsletter_content="md",
        articles=articles,
        recommended_articles=[],
        execution_time_seconds=12.0,
        token_usage={"prompt_tokens": 10, "completion_tokens": 5},
        timings={},
        metrics={},
        trust_metrics=TrustMetrics(
            grounding_reliability_pct=grounding,
            validation_success_rate=validation,
            source_diversity_healthy=True,
            hallucination_rejections=0,
            total_signals_processed=len(articles),
        ),
    )


def test_empty_articles_sqi_is_zero():
    briefing = persistence_service.save_briefing(MagicMock(), "u", _response([]))
    assert briefing.signal_quality_index == 0.0
    assert briefing.title == "InsightGraph Digest"


def test_sqi_formula():
    arts = [_article(title="A", trend_score=4.0), _article(title="B", trend_score=6.0)]
    briefing = persistence_service.save_briefing(MagicMock(), "u", _response(arts, grounding=90.0, validation=80.0))
    # avg_trend=5 -> normalized=25 ; 90*.4 + 80*.3 + 25*.3 = 67.5
    assert briefing.signal_quality_index == 67.5


def test_dominant_topics_and_dynamic_title():
    arts = [
        _article(title="A", tags=["Agents", "Agents", "LLMs"]),
        _article(title="B", tags=["Agents", "LLMs"]),
    ]
    briefing = persistence_service.save_briefing(MagicMock(), "u", _response(arts))
    assert briefing.dominant_topics[:2] == ["Agents", "LLMs"]
    assert briefing.title == "InsightGraph Digest: Agents & LLMs"


def test_matched_topics_and_sources_parsed_from_reasons():
    arts = [
        _article(
            title="A",
            recommendation_reasons=["Matches preferred topic: Open Source AI (+3.0)", "Preferred source: rss (+2.0)"],
        )
    ]
    briefing = persistence_service.save_briefing(MagicMock(), "u", _response(arts))
    assert briefing.matched_topics == ["Open Source AI"]
    assert briefing.matched_sources == ["rss"]
