"""End-to-end wiring of the LangGraph pipeline with every external boundary mocked."""
import pytest

from agents import analyzer as analyzer_mod
from agents import composer as composer_mod
from agents import retriever as retriever_mod
from agents import validator as validator_mod
from agents.analyzer import ArticleAnalysis
from graphs.newsletter_graph import create_newsletter_graph
from models.state import PipelineState
from models.user import UserPreferences, UserProfile


def test_graph_compiles():
    assert create_newsletter_graph() is not None


class _Msg:
    def __init__(self, content):
        self.content = content
        self.response_metadata = {"token_usage": {"prompt_tokens": 5, "completion_tokens": 3}}


class _FakeChat:
    """Stands in for ChatGroq across validator / analyzer / composer."""

    def __init__(self, *a, **k):
        pass

    async def ainvoke(self, *a, **k):  # validator
        return _Msg("YES")

    def invoke(self, *a, **k):  # composer editorial intro
        return _Msg("An editorial intro sentence.")

    def with_structured_output(self, *a, **k):  # analyzer
        def _run(*_a, **_k):
            return {
                "parsed": ArticleAnalysis(
                    summary="AI model update analysis with plenty of words to clear the ten word minimum",
                    details=["First detail sentence that is long enough.", "Second detail sentence here."],
                    why_it_matters="This matters a great deal for the whole AI ecosystem and its participants.",
                    tags=["AI"],
                ),
                "raw": _Msg(""),
            }

        return _run


@pytest.fixture
def mocked_pipeline(monkeypatch):
    def raw(i):
        return {
            "title": f"AI model update {i}",
            "url": f"https://x/{i}",
            "content": "story body about an AI model update",
            "source": "tavily",
            "stars": 1000,  # -> ranker adds log10(1000)=3.0, keeps avg_trend_score >= 2.0
        }

    monkeypatch.setattr(retriever_mod, "fetch_ai_news", lambda **k: [raw(i) for i in range(8)])
    monkeypatch.setattr(retriever_mod, "fetch_arxiv_papers", lambda **k: [])
    monkeypatch.setattr(retriever_mod, "fetch_hacker_news", lambda **k: [])
    monkeypatch.setattr(retriever_mod, "fetch_rss_feeds", lambda **k: [])
    monkeypatch.setattr(validator_mod, "ChatGroq", _FakeChat)
    monkeypatch.setattr(analyzer_mod, "ChatGroq", _FakeChat)
    monkeypatch.setattr(composer_mod, "ChatGroq", _FakeChat)
    monkeypatch.setattr(analyzer_mod.memory_manager, "get_historical_context", lambda *a, **k: [])


async def test_full_run_produces_a_newsletter(mocked_pipeline):
    graph = create_newsletter_graph()
    profile = UserProfile(user_id="u", preferences=UserPreferences(preferred_topics=[], excluded_topics=[]))

    final = await graph.ainvoke(PipelineState(user_profile=profile))
    state = PipelineState(**final)

    assert state.pipeline_stage == "composition"
    assert state.final_newsletter and state.final_newsletter.startswith("# InsightGraph Digest")
    assert len(state.articles) >= 6
    assert all(a.summary and a.summary != "Summary generation failed." for a in state.articles)
    assert "## Top Stories" in state.final_newsletter
