"""Pure logic of agents/ranker.py — word-boundary topic matching and scoring."""
from agents.ranker import _topic_hits, rank_articles
from config.settings import MAX_ARTICLES_TO_ANALYZE


class TestTopicHits:
    def test_whole_phrase_match(self):
        assert _topic_hits("Large Language Models", "New large language models shipped") is True

    def test_single_significant_token_match(self):
        assert _topic_hits("AI Hardware & Chips", "TSMC ramps chips output") is True

    def test_word_boundary_prevents_substring_false_positive(self):
        # regression: "sports" must not match "transports" / "esports"
        assert _topic_hits("Sports", "New transports and esports coverage") is False

    def test_no_match(self):
        assert _topic_hits("Crypto & Blockchain", "A story about world models") is False

    def test_stopword_only_topic_never_matches(self):
        assert _topic_hits("the and for", "the quick brown fox") is False

    def test_empty_topic(self):
        assert _topic_hits("", "anything") is False

    def test_short_tokens_ignored(self):
        # "NFTs" normalizes to "nfts" (4 chars) -> only the whole phrase can match
        assert _topic_hits("NFTs", "the market for nfts") is True
        assert _topic_hits("NFTs", "nft market news") is False


class TestRankArticles:
    def test_excluded_topic_hard_drop_on_title(self, make_state, make_article):
        keep = make_article(title="LLM breakthrough", content="model news")
        drop = make_article(title="Sports roundup weekly", content="scores")
        profile_state = make_state(articles=[keep, drop])
        profile_state.user_profile.preferences.excluded_topics = ["Sports"]

        out = rank_articles(profile_state)

        titles = [a.title for a in out.articles]
        assert "LLM breakthrough" in titles
        assert "Sports roundup weekly" not in titles

    def test_excluded_topic_only_checks_title_plus_lede_not_full_body(self, make_state, make_article):
        # regression: a mention deep in the body must NOT drop the article
        body = "Real AI news. " + ("filler " * 60) + "the word gaming appears here far in"
        art = make_article(title="Nvidia data-center GPUs", content=body)
        state = make_state(articles=[art])
        state.user_profile.preferences.excluded_topics = ["Gaming"]

        out = rank_articles(state)

        assert [a.title for a in out.articles] == ["Nvidia data-center GPUs"]

    def test_preferred_topic_and_source_boosts(self, make_state, make_article):
        art = make_article(title="Open Source AI wins", content="oss models", source="rss")
        state = make_state(articles=[art])
        state.user_profile.preferences.preferred_topics = ["Open Source AI"]
        state.user_profile.preferences.preferred_sources = ["rss"]

        out = rank_articles(state)

        # base 1.0 + topic 3.0 + source 2.0
        assert out.articles[0].trend_score == 6.0
        assert out.articles[0].personalization_boost == 5.0
        assert any("Open Source AI" in r for r in out.articles[0].recommendation_reasons)

    def test_breakthrough_keyword_and_stars(self, make_state, make_article):
        art = make_article(title="X", content="a state-of-the-art result", stars=100)
        state = make_state(articles=[art])

        out = rank_articles(state)

        # base 1.0 + keyword 2.0 + log10(100)=2.0
        assert out.articles[0].trend_score == 5.0

    def test_sorted_desc_and_truncated(self, make_state, make_article):
        arts = [make_article(title=f"t{i}", content="c", stars=(i + 1) * 10) for i in range(20)]
        out = rank_articles(make_state(articles=arts))

        assert len(out.articles) == MAX_ARTICLES_TO_ANALYZE
        scores = [a.trend_score for a in out.articles]
        assert scores == sorted(scores, reverse=True)
