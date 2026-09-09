"""models/state.py + models/user.py — construction defaults."""
from models.state import Article, PipelineMetadata, PipelineState
from models.user import (
    DEFAULT_EXCLUDED_TOPICS,
    DEFAULT_PREFERRED_TOPICS,
    UserPreferences,
    UserProfile,
)


def test_pipeline_state_no_args():
    s = PipelineState()
    assert s.articles == []
    assert s.pipeline_stage == "initialized"
    assert s.retry_count == 0
    assert s.max_retries == 1
    assert s.final_newsletter is None
    assert s.user_profile is None


def test_pipeline_metadata_token_limit_defaults_false():
    assert PipelineMetadata().token_limit_hit is False


def test_article_minimal_constructor():
    a = Article(title="t", url="u", content="c", source="tavily")
    assert a.trend_score == 0.0
    assert a.personalization_boost == 0.0
    assert a.tags == []
    assert a.grounding_verified is False


def test_user_profile_populates_default_topics():
    p = UserProfile(user_id="abc")
    assert p.preferences.preferred_topics == DEFAULT_PREFERRED_TOPICS
    assert p.preferences.excluded_topics == DEFAULT_EXCLUDED_TOPICS
    assert p.preferences.email_delivery_enabled is True


def test_user_preferences_defaults_are_copies_not_shared():
    a = UserPreferences()
    a.preferred_topics.append("mutated")
    b = UserPreferences()
    assert "mutated" not in b.preferred_topics
