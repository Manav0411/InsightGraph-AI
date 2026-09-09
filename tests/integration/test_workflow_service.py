"""backend/services/workflow_service.py::run_newsletter_workflow — mapping + guard."""
import pytest

from backend.schemas.requests import NewsletterRequest
from backend.services import workflow_service
from models.state import Article, PipelineState


def _install_graph(monkeypatch, final_state: PipelineState):
    class StubGraph:
        async def ainvoke(self, _state):
            return final_state.model_dump()

    monkeypatch.setattr(workflow_service, "create_newsletter_graph", lambda: StubGraph())
    monkeypatch.setattr(workflow_service, "save_last_run", lambda *_a, **_k: None)


@pytest.fixture
def request_and_profile(make_user_profile):
    return NewsletterRequest(user_id="u"), make_user_profile()


async def test_raises_when_no_articles(monkeypatch, request_and_profile):
    req, profile = request_and_profile
    state = PipelineState(final_newsletter="# InsightGraph Digest\n")  # zero articles
    state.errors.append("everything failed")
    _install_graph(monkeypatch, state)

    with pytest.raises(RuntimeError, match="no valid articles"):
        await workflow_service.run_newsletter_workflow(req, profile)


async def test_maps_state_to_response(monkeypatch, request_and_profile):
    req, profile = request_and_profile
    arts = [
        Article(title="A", url="u1", content="c", source="tavily", summary="s", why_it_matters="w",
                tags=["T"], details=["d1", "d2"], trend_score=4.0, personalization_boost=3.0),
        Article(title="B", url="u2", content="c", source="rss", summary="s2", why_it_matters="w2",
                tags=["T"], details=["d1", "d2"], trend_score=2.0),
    ]
    state = PipelineState(articles=arts, final_newsletter="# InsightGraph Digest\n\nbody")
    state.metadata.total_prompt_tokens = 100
    state.metadata.total_completion_tokens = 40
    state.metadata.total_articles_processed = 2
    state.metadata.retrieval_sources = ["tavily", "rss"]
    _install_graph(monkeypatch, state)

    resp = await workflow_service.run_newsletter_workflow(req, profile)

    assert len(resp.articles) == 2
    assert resp.newsletter_content.startswith("# InsightGraph Digest")
    assert resp.token_usage == {"prompt_tokens": 100, "completion_tokens": 40}
    assert [a.title for a in resp.recommended_articles] == ["A"]  # only boosted
    assert resp.trust_metrics.source_diversity_healthy is True
