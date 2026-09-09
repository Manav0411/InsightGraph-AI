"""Pure logic of agents/evaluator.py — rejection rules and diversity trim."""
import pytest

from agents.evaluator import evaluate_newsletter
from config.settings import MIN_SUMMARY_WORDS, TARGET_FINAL_ARTICLES


VALID_SUMMARY = "Alpha beta gamma model launched today with strong benchmark results across many domains and tasks"
VALID_WHY = "It shifts the competitive landscape for foundation model providers meaningfully."


@pytest.fixture
def valid_article(make_article):
    def _make(**over):
        base = dict(
            title="Alpha Beta Gamma model",
            summary=VALID_SUMMARY,
            why_it_matters=VALID_WHY,
            tags=["Models", "Benchmarks"],
            details=["First concrete detail sentence.", "Second concrete detail sentence."],
            trend_score=3.0,
        )
        base.update(over)
        return make_article(**base)

    return _make


def _titles(state):
    return [a.title for a in state.articles]


class TestRejectionRules:
    def test_all_valid_passes(self, make_state, valid_article):
        out = evaluate_newsletter(make_state(articles=[valid_article()]))
        assert _titles(out) == ["Alpha Beta Gamma model"]
        assert out.metadata.total_articles_rejected == 0

    def test_empty_input_early_return(self, make_state):
        out = evaluate_newsletter(make_state(articles=[]))
        assert out.articles == []
        assert any("empty article list" in w for w in out.warnings)

    def test_failed_summary_sentinel_removed(self, make_state, valid_article):
        out = evaluate_newsletter(make_state(articles=[valid_article(summary="Summary generation failed.")]))
        assert out.articles == []
        assert out.metadata.total_articles_rejected == 1

    def test_analysis_failed_why_removed(self, make_state, valid_article):
        out = evaluate_newsletter(make_state(articles=[valid_article(why_it_matters="Analysis failed.")]))
        assert out.articles == []

    def test_duplicate_title_removed(self, make_state, valid_article):
        out = evaluate_newsletter(make_state(articles=[valid_article(), valid_article()]))
        assert len(out.articles) == 1
        assert out.metadata.total_articles_rejected == 1

    def test_missing_tags_removed(self, make_state, valid_article):
        out = evaluate_newsletter(make_state(articles=[valid_article(tags=[])]))
        assert out.articles == []

    def test_short_summary_removed(self, make_state, valid_article):
        short = " ".join(["word"] * (MIN_SUMMARY_WORDS - 1))
        out = evaluate_newsletter(make_state(articles=[valid_article(summary=short)]))
        assert out.articles == []

    def test_buzzword_summary_removed(self, make_state, valid_article):
        bad = "This alpha model will transform the future of everything we know about computing today"
        out = evaluate_newsletter(make_state(articles=[valid_article(summary=bad)]))
        assert out.articles == []

    def test_short_why_it_matters_removed(self, make_state, valid_article):
        out = evaluate_newsletter(make_state(articles=[valid_article(why_it_matters="Too short.")]))
        assert out.articles == []

    def test_too_few_details_removed(self, make_state, valid_article):
        out = evaluate_newsletter(make_state(articles=[valid_article(details=["only one"])]))
        assert out.articles == []

    def test_low_trend_score_removed(self, make_state, valid_article):
        out = evaluate_newsletter(make_state(articles=[valid_article(trend_score=0.5)]))
        assert out.articles == []

    def test_ungrounded_summary_removed_and_counted(self, make_state, valid_article):
        # >=10 words but shares zero keywords (alpha/beta/gamma/model) with the title
        ungrounded = "Completely unrelated discussion about weather patterns over oceans and coastal regions during winter seasons"
        out = evaluate_newsletter(make_state(articles=[valid_article(summary=ungrounded)]))
        assert out.articles == []
        assert out.metadata.grounding_rejections == 1


class TestDiversityTrim:
    def test_no_trim_at_or_below_target(self, make_state, valid_article):
        arts = [valid_article(title=f"Alpha model number {i}") for i in range(TARGET_FINAL_ARTICLES)]
        out = evaluate_newsletter(make_state(articles=arts))
        assert len(out.articles) == TARGET_FINAL_ARTICLES

    def test_trims_to_target_with_source_spread(self, make_state, valid_article):
        arts = []
        for i in range(8):
            arts.append(valid_article(title=f"Alpha tavily story {i}", source="tavily", trend_score=5.0 + i))
        for i in range(8):
            arts.append(valid_article(title=f"Alpha rss story {i}", source="rss", trend_score=1.5))

        out = evaluate_newsletter(make_state(articles=arts))

        assert len(out.articles) == TARGET_FINAL_ARTICLES
        sources = {a.source for a in out.articles}
        assert sources == {"tavily", "rss"}  # both represented, not all-tavily
        scores = [a.trend_score for a in out.articles]
        assert scores == sorted(scores, reverse=True)
