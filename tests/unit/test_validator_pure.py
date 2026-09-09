"""agents/validator.py pure helpers — prompt shape and fail-open parsing."""
import pytest

from agents.validator import _build_prompt, _parse_relevance


class TestParseRelevance:
    @pytest.mark.parametrize("text", ["YES", "yes", "Yes, relevant", "  YES\n"])
    def test_yes_keeps(self, text):
        assert _parse_relevance(text) is True

    @pytest.mark.parametrize("text", ["NO", "No.", "No, this is unrelated", "no"])
    def test_no_drops(self, text):
        assert _parse_relevance(text) is False

    def test_empty_fails_open(self):
        assert _parse_relevance("") is True
        assert _parse_relevance(None) is True

    def test_ambiguous_fails_open(self):
        assert _parse_relevance("The article seems fine to me") is True

    def test_no_far_into_text_is_ignored(self):
        # only the first 20 chars are inspected
        assert _parse_relevance("This looks relevant and on topic, no complaints") is True


class TestBuildPrompt:
    def test_hacker_news_branch(self, make_article):
        p = _build_prompt(make_article(source="hacker_news", title="Show HN: my LLM tool"))
        assert "Hacker News post" in p
        assert "Show HN: my LLM tool" in p
        assert "Content snippet" not in p

    def test_default_branch_includes_lede_only(self, make_article):
        art = make_article(source="tavily", title="Big model release", content="X" * 500)
        p = _build_prompt(art)
        assert "Content snippet (first 300 chars)" in p
        assert "X" * 300 in p
        assert "X" * 301 not in p
