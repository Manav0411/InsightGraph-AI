"""agents/analyzer.py — happy path, skip-already-analyzed, and TPD token-limit handling.

The Groq LLM is mocked at agents.analyzer.ChatGroq. `with_structured_output(...)`
returns a plain callable, so the real `prompt | structured` pipe still composes into
a RunnableSequence whose `.invoke()` calls our fake.
"""
import pytest

from agents import analyzer
from agents.analyzer import ArticleAnalysis, analyze_articles


class _Raw:
    response_metadata = {"token_usage": {"prompt_tokens": 12, "completion_tokens": 7}}


def _good_result():
    return {
        "parsed": ArticleAnalysis(
            summary="Grounded summary.",
            details=["d1", "d2", "d3"],
            why_it_matters="It matters.",
            tags=["Models"],
        ),
        "raw": _Raw(),
    }


@pytest.fixture
def install_llm(monkeypatch):
    """Patch ChatGroq + memory_manager. `behaviour(prompt_value)` drives every chain.invoke."""

    def _install(behaviour):
        class FakeChat:
            def __init__(self, *a, **k):
                pass

            def with_structured_output(self, *a, **k):
                return behaviour

            def invoke(self, *a, **k):  # composer-style direct call (unused here)
                return behaviour(*a, **k)

        monkeypatch.setattr(analyzer, "ChatGroq", FakeChat)
        monkeypatch.setattr(
            analyzer.memory_manager, "get_historical_context", lambda *a, **k: []
        )

    return _install


def test_happy_path_fills_fields_and_tokens(make_state, make_article, install_llm):
    install_llm(lambda *_a, **_k: _good_result())
    art = make_article(title="Story", source="tavily", content="body")

    out = analyze_articles(make_state(articles=[art]))

    a = out.articles[0]
    assert a.summary == "Grounded summary."
    assert a.details == ["d1", "d2", "d3"]
    assert a.tags == ["Models"]
    assert out.metadata.total_articles_processed == 1
    assert out.metadata.total_prompt_tokens == 12
    assert out.metadata.total_completion_tokens == 7
    assert out.metadata.token_limit_hit is False


def test_skips_already_analyzed(make_state, make_article, install_llm):
    hits = []
    install_llm(lambda *_a, **_k: hits.append(1) or _good_result())
    done = make_article(title="Done", summary="already summarized text", source="tavily")

    out = analyze_articles(make_state(articles=[done]))

    assert hits == []  # LLM never called
    assert out.articles[0].summary == "already summarized text"
    assert out.metadata.total_articles_processed == 1


def test_token_limit_marks_flag_and_fails_article(make_state, make_article, install_llm):
    def raise_tpd(*_a, **_k):
        # 429 with no "try again in Ns" -> analyzer treats as daily-token limit
        raise Exception("Error code: 429 - rate_limit_exceeded: tokens per day (TPD)")

    install_llm(raise_tpd)
    art = make_article(title="Blocked", source="tavily")  # tavily -> already on fast model

    out = analyze_articles(make_state(articles=[art]))

    assert out.articles[0].summary == "Summary generation failed."
    assert out.metadata.token_limit_hit is True


def test_missing_groq_key_returns_early(make_state, make_article, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    out = analyze_articles(make_state(articles=[make_article()]))
    assert any("GROQ_API_KEY" in e for e in out.errors)
