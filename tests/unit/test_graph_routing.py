"""graphs/newsletter_graph.py::route_after_evaluation — recovery routing."""
from agents.evaluator import evaluate_newsletter  # noqa: F401  (keep import graph warm)
from graphs.newsletter_graph import route_after_evaluation
from config.settings import MIN_VIABLE_ARTICLES


def _articles(make_article, n, source="tavily", score=3.0):
    return [make_article(title=f"t{i}", source=source, trend_score=score) for i in range(n)]


def test_token_limit_hit_short_circuits_to_composer(make_state, make_article):
    state = make_state(articles=_articles(make_article, 3))  # thin, would normally recover
    state.metadata.token_limit_hit = True
    state.retry_count = 0

    assert route_after_evaluation(state) == "composer"


def test_thin_result_triggers_recovery(make_state, make_article):
    state = make_state(articles=_articles(make_article, MIN_VIABLE_ARTICLES - 1))
    state.retry_count = 0

    assert route_after_evaluation(state) == "retriever"


def test_near_complete_run_ships_without_wasteful_recovery(make_state, make_article):
    # regression: 7 solid tavily articles should NOT trigger a recovery lap
    state = make_state(articles=_articles(make_article, 7, score=4.0))
    state.retry_count = 0

    assert route_after_evaluation(state) == "composer"


def test_recovery_budget_exhausted_goes_to_composer(make_state, make_article):
    state = make_state(articles=_articles(make_article, 2))
    state.retry_count = 1
    state.max_retries = 1

    assert route_after_evaluation(state) == "composer"


def test_no_tavily_source_triggers_recovery(make_state, make_article):
    state = make_state(articles=_articles(make_article, 8, source="rss", score=4.0))
    state.retry_count = 0

    assert route_after_evaluation(state) == "retriever"


def test_low_avg_trend_score_triggers_recovery(make_state, make_article):
    state = make_state(articles=_articles(make_article, 8, score=1.0))
    state.retry_count = 0

    assert route_after_evaluation(state) == "retriever"
