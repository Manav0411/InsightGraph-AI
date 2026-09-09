# Backend test suite

Fast, hermetic pytest suite — no network, no real LLM, no real database.

```bash
pip install -r requirements-dev.txt
pytest                 # ~1.5s, 98 tests
pytest tests/unit -q   # just the pure-function layer
```

Config lives in `pyproject.toml` (`[tool.pytest.ini_options]`): `pythonpath = ["."]`
replicates "run from the repo root", and `asyncio_mode = "auto"` means `async def test_…`
needs no decorator.

## Layout

| Dir | What |
|---|---|
| `unit/` | Pure functions — `ranker._topic_hits` / `rank_articles`, `evaluator`, `newsletter_graph.route_after_evaluation`, `validator` parse helpers, `content_cleaner`, state models. Includes a regression anchor for every bug fixed in the Sept 2026 round. |
| `agents/` | `retriever` (services mocked), `analyzer` (`ChatGroq` + `memory_manager` mocked), `composer` (LLM intro skipped via unset key). |
| `services/` | `arxiv` / `rss` / `hacker_news` / `tavily` parsing, driven by fixture data with `urlopen` / `TavilyClient` patched. |
| `integration/` | `test_graph_smoke` — full `graph.ainvoke()` with every boundary mocked. `test_workflow_service` — `run_newsletter_workflow` mapping + the raise-on-empty guard. |
| `backend/` | `save_briefing` SQI math (MagicMock session); route auth guards via `TestClient` + `dependency_overrides`. |

## Conventions

- `tests/conftest.py` sets dummy env (`DATABASE_URL`, `GROQ_API_KEY`, …) **before** any
  project import — several modules read env / build a SQLAlchemy engine at import time.
- Factory fixtures: `make_article`, `make_state`, `make_user_profile`.
- An autouse fixture no-ops `time.sleep` so retry/throttle paths run instantly.
- Mock at the *importing* module: `agents.validator.ChatGroq`, `services.arxiv_service.urllib.request.urlopen`, etc.
