"""
Shared test setup.

The env vars below MUST be set before any project module is imported: several
modules read env / build a SQLAlchemy engine at import time. `create_engine`
with a syntactically valid postgres URL is lazy and never connects, so a dummy
value is enough to make imports succeed offline.
"""
import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("TAVILY_API_KEY", "test-tavily-key")
os.environ.setdefault("HF_TOKEN", "test-hf-token")
os.environ.setdefault("CRON_SECRET", "test-cron-secret")
os.environ.setdefault("ADMIN_EMAILS", "admin@example.com")

import time

import pytest

from models.state import Article, PipelineState
from models.user import UserPreferences, UserProfile


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Keep retry/throttle waits from actually sleeping."""
    monkeypatch.setattr(time, "sleep", lambda *_a, **_k: None)


@pytest.fixture
def make_article():
    def _make(**over):
        base = dict(title="A Title", url="https://example.com/a", content="body text", source="tavily")
        base.update(over)
        return Article(**base)

    return _make


@pytest.fixture
def make_user_profile():
    def _make(preferred_topics=None, excluded_topics=None, preferred_sources=None, user_id="test-user"):
        prefs = UserPreferences(
            preferred_topics=preferred_topics if preferred_topics is not None else [],
            excluded_topics=excluded_topics if excluded_topics is not None else [],
            preferred_sources=preferred_sources if preferred_sources is not None else [],
        )
        return UserProfile(user_id=user_id, preferences=prefs)

    return _make


@pytest.fixture
def make_state(make_user_profile):
    def _make(articles=None, user_profile=None, **over):
        state = PipelineState(
            articles=list(articles) if articles else [],
            user_profile=user_profile if user_profile is not None else make_user_profile(),
        )
        for k, v in over.items():
            setattr(state, k, v)
        return state

    return _make
