"""agents/retriever.py — normalization, dedup, and recovery scaling (services mocked)."""
import pytest

from agents import retriever
from config.settings import ARXIV_MAX_RESULTS


def _raw(title, source, **over):
    d = {"title": title, "url": f"https://x/{title}", "content": "c", "source": source}
    d.update(over)
    return d


@pytest.fixture
def patch_sources(monkeypatch):
    calls = {}

    def make(name, ret):
        def fn(**kwargs):
            calls[name] = kwargs
            return ret

        return fn

    def _apply(tavily=None, arxiv=None, hn=None, rss=None):
        monkeypatch.setattr(retriever, "fetch_ai_news", make("tavily", tavily or []))
        monkeypatch.setattr(retriever, "fetch_arxiv_papers", make("arxiv", arxiv or []))
        monkeypatch.setattr(retriever, "fetch_hacker_news", make("hn", hn or []))
        monkeypatch.setattr(retriever, "fetch_rss_feeds", make("rss", rss or []))
        return calls

    return _apply


def test_normalizes_raw_dicts_to_articles(make_state, patch_sources):
    patch_sources(
        tavily=[_raw("News A", "tavily", image_url="http://img")],
        arxiv=[_raw("Paper B", "arxiv")],
        hn=[_raw("HN C", "hacker_news", stars=88)],
    )
    out = retriever.retrieve_articles(make_state())

    by_title = {a.title: a for a in out.articles}
    assert set(by_title) == {"News A", "Paper B", "HN C"}
    assert by_title["News A"].image_url == "http://img"
    assert by_title["HN C"].stars == 88
    assert set(out.metadata.retrieval_sources) == {"tavily", "arxiv", "hacker_news"}
    assert out.metadata.total_articles_retrieved == 3


def test_dedup_by_lowercased_title_including_existing(make_state, make_article, patch_sources):
    existing = make_article(title="Shared Story")
    patch_sources(
        tavily=[_raw("shared story", "tavily"), _raw("Fresh One", "tavily"), _raw("FRESH ONE", "tavily")],
    )
    out = retriever.retrieve_articles(make_state(articles=[existing]))

    titles = sorted(a.title for a in out.articles)
    assert titles == ["Fresh One", "Shared Story"]  # dup of existing + internal dup dropped


def test_one_service_failing_does_not_abort_others(make_state, monkeypatch, patch_sources):
    patch_sources(arxiv=[_raw("Paper", "arxiv")])

    def boom(**_):
        raise RuntimeError("tavily down")

    monkeypatch.setattr(retriever, "fetch_ai_news", boom)
    out = retriever.retrieve_articles(make_state())

    assert [a.title for a in out.articles] == ["Paper"]
    assert any("Tavily retrieval failed" in e for e in out.errors)


def test_recovery_reentry_bumps_counters_and_scales_limits(make_state, patch_sources):
    calls = patch_sources()
    state = make_state()
    state.pipeline_stage = "evaluation"  # simulate Evaluator -> Retriever
    state.metadata.recovery_attempts = 1  # already one lap in

    retriever.retrieve_articles(state)

    assert state.retry_count == 1
    assert state.metadata.recovery_attempts == 2
    assert state.metadata.conditional_routes_triggered == 1
    # limits scale with recovery_attempts (2): tavily/hn = 5 + 2*3 = 11, arxiv = 10 + 2*2 = 14
    assert calls["tavily"]["max_results"] == 11
    assert calls["hn"]["max_results"] == 11
    assert calls["arxiv"]["max_results"] == ARXIV_MAX_RESULTS + 4


def test_preferred_topics_passed_through_as_queries(make_state, make_user_profile, patch_sources):
    calls = patch_sources()
    profile = make_user_profile(preferred_topics=["Agents", "RAG"])
    retriever.retrieve_articles(make_state(user_profile=profile))

    assert calls["tavily"]["queries"] == ["Agents", "RAG"]
    assert calls["arxiv"]["topics"] == ["Agents", "RAG"]
