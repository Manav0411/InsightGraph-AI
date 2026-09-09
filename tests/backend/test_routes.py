"""FastAPI route tests — auth guards on the cron/scheduler paths + /latest empty case.

TestClient is used WITHOUT a `with` block so app lifespan (DB connect on startup)
does not run.
"""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.db.database import get_db
from backend.dependencies.auth import get_current_user
from backend.routes import scheduler as scheduler_route
from backend.services import persistence_service


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: "test-user"
    app.dependency_overrides[get_db] = lambda: MagicMock()
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestSchedulerRunNow:
    def test_wrong_secret_401(self, client):
        r = client.post("/scheduler/run-now", headers={"X-Cron-Secret": "nope"})
        assert r.status_code == 401

    def test_missing_server_secret_500(self, client, monkeypatch):
        monkeypatch.delenv("CRON_SECRET", raising=False)
        r = client.post("/scheduler/run-now", headers={"X-Cron-Secret": "anything"})
        assert r.status_code == 500

    def test_all_failed_returns_502(self, client, monkeypatch):
        async def fake_run():
            return {"processed": 2, "succeeded": 0, "failed": 2, "failures": []}

        monkeypatch.setattr(scheduler_route, "daily_intelligence_generation", fake_run)
        r = client.post("/scheduler/run-now", headers={"X-Cron-Secret": "test-cron-secret"})
        assert r.status_code == 502

    def test_success_returns_summary(self, client, monkeypatch):
        async def fake_run():
            return {"processed": 1, "succeeded": 1, "failed": 0, "failures": []}

        monkeypatch.setattr(scheduler_route, "daily_intelligence_generation", fake_run)
        r = client.post("/scheduler/run-now", headers={"X-Cron-Secret": "test-cron-secret"})
        assert r.status_code == 200
        assert r.json()["summary"]["succeeded"] == 1


class TestGenerateAutonomous:
    def test_requires_cron_secret(self, client):
        r = client.post("/newsletter/generate-autonomous/some-user")
        assert r.status_code == 401


class TestLatest:
    def test_404_when_no_briefing(self, client, monkeypatch):
        monkeypatch.setattr(persistence_service, "fetch_latest_briefing", lambda *a, **k: None)
        r = client.get("/newsletter/latest")
        assert r.status_code == 404
