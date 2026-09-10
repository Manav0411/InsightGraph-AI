# InsightGraph

**You slept. It read everything. Here are the twelve.**

InsightGraph is a personal AI-ecosystem briefing. Overnight, a six-agent
LangGraph pipeline reads the day's AI news, research and community chatter,
ranks it against the topics you care about, grounds every claim against a
source, and files one dated briefing — on the web and in your inbox by 8 AM.

![The morning briefing — a dated document of ranked, source-grounded signals](docs/screenshots/reader.jpg)

---

## What it does

- **Reads a fixed set of sources every night** — Tavily news, Hacker News,
  arXiv (`cs.AI` / `cs.CL` / `cs.LG`) and lab RSS (Hugging Face, VentureBeat,
  MIT Technology Review) — deduped into one candidate set.
- **Ranks the day against *your* topics.** Ten topics chosen at onboarding
  get a fixed boost in the ranker; an exclusion list is dropped *before* the
  analyzer spends a token on it.
- **Grounds, doesn't vibe.** A fast validator drops clickbait; the evaluator
  prunes weak generations and checks each summary against its headline.
  Anything that can't be grounded against a source is cut.
- **Remembers.** Past briefings are embedded into Postgres (`pgvector`), so
  the analyzer can frame a new signal against its precedent.
- **Delivers one document**, not a link dump: each signal is a summary, the
  concrete details, and *why it matters*. Plus a searchable archive and an
  admin console with real pipeline telemetry (SQI, grounding, latency,
  token spend).

---

## How it works

Each briefing is **one traversal of a LangGraph state machine**
(`graphs/newsletter_graph.py`):

```
retriever → validator → ranker → analyzer → evaluator → (composer | retriever)
composer  → END
```

![The pipeline — six agents, with the evaluator able to route back to the retriever once](docs/screenshots/pipeline-graph.jpg)

| Stage | What it does |
|-------|--------------|
| **retriever** | Pulls from Tavily, Hacker News, arXiv and lab RSS; dedupes into one set. Scales its search limits up on a recovery lap. |
| **validator** | Fast yes/no relevance pass. Drops clickbait. Fails open on rate limits so a flaky LLM never stalls the run. |
| **ranker** | Trend score, then your topic boosts and hard exclusions (word-boundary matched on title + lede). |
| **analyzer** | Grounded summary, details and "why it matters" for each survivor — with vector-memory context from past briefings. |
| **evaluator** | Prunes weak generations, checks summary vs. headline, balances sources. Then **decides**: proceed, or send the run back. |
| **composer** | Assembles the digest, writes the intro, files it to the archive and the delivery queue. |

**The one edge that runs backwards.** `route_after_evaluation` sends the run
back to the **retriever** — once — if the result is too thin
(`< MIN_VIABLE_ARTICLES`), has no Tavily coverage, or has a low average trend
score. If the daily Groq token budget is already spent, it skips recovery and
ships what it has rather than failing the same way twice.

---

## Tech stack

| Layer | Choices |
|-------|---------|
| **Frontend** | Next.js 16 (App Router, React 19), TailwindCSS v3, Clerk auth. A shared design system lives in `frontend/src/components/ui/` — see `frontend/DESIGN.md`. |
| **Backend** | FastAPI, SQLAlchemy, Postgres (Neon serverless) with `pgvector` |
| **AI orchestration** | LangGraph state machine, Groq inference (`openai/gpt-oss-20b` / `gpt-oss-120b`), optional LangSmith tracing |
| **Delivery & scheduling** | Vercel (frontend), Render (backend), GitHub Actions cron → `POST /scheduler/run-now` |
| **Tests** | `pytest` — 98 hermetic tests, no network / LLM / DB. `pip install -r requirements-dev.txt && pytest` |

---

## Project structure

```text
ai_trend_intelligence/
├── agents/                 # The six pipeline agents
│   ├── retriever.py  validator.py  ranker.py
│   └── analyzer.py   evaluator.py  composer.py
├── graphs/
│   └── newsletter_graph.py # The LangGraph state machine + routing
├── services/               # Source clients (tavily, hacker_news, arxiv, rss)
├── models/                 # Pydantic pipeline state + SQLAlchemy DB models
├── prompts/                # LLM system prompts, decoupled from code
├── config/                 # settings.py (thresholds), models.py (model ids)
├── backend/
│   ├── main.py             # FastAPI app + CORS
│   ├── routes/             # newsletter, users, analytics, scheduler, …
│   ├── services/           # task manager, workflow runner, vector store, email
│   ├── dependencies/       # Clerk JWT verification
│   └── db/                 # engine + session
├── frontend/
│   ├── DESIGN.md           # The "Warm Editorial" design system
│   └── src/
│       ├── app/            # Routes: / (landing or reader), history, preferences,
│       │                   #         onboarding, admin/{mission-control,analytics}
│       ├── components/
│       │   ├── ui/         # Design-system primitives (Button, Card, Chip, …)
│       │   ├── landing/    # Public marketing page
│       │   └── IntelligenceReader.js
│       ├── context/  lib/  proxy.js
│       └── ...
├── tests/                  # pytest suite (unit, agents, services, integration)
├── .github/workflows/      # cron.yml — nightly trigger
├── requirements.txt        # pinned prod deps  ·  requirements-dev.txt — test deps
└── runtime.txt / .python-version   # Python 3.13
```

---

## Running locally

### 1. Backend

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the repo root:

```env
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key
RESEND_API_KEY=your_key
DATABASE_URL=postgresql://user:password@host/dbname   # needs the pgvector extension

CLERK_JWKS_URL=https://<your-subdomain>.clerk.accounts.dev/.well-known/jwks.json
FRONTEND_URL=http://localhost:3000

# optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=InsightGraph
```

```bash
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL=/
NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL=/onboarding
NEXT_PUBLIC_CLERK_AFTER_SIGN_OUT_URL=/

# where the frontend calls the backend — the local backend, or the deployed one
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
ADMIN_EMAILS=you@example.com
NEXT_PUBLIC_ADMIN_EMAILS=you@example.com
```

```bash
npm run dev
```

Sign in, pick topics at onboarding, and the first run kicks off. On a fresh
account with no briefing yet, `/` shows the public landing; once a briefing
exists it shows the reader.

### 3. Deployment

- **Frontend → Vercel.** Set `NEXT_PUBLIC_API_URL` to the Render backend URL
  and the Clerk keys to their production values.
- **Backend → Render** (web service). Set `FRONTEND_URL` to the Vercel domain
  so CORS allows it, plus a `CRON_SECRET` for the scheduler route.
- **Scheduling → GitHub Actions.** `.github/workflows/cron.yml` posts to
  `/scheduler/run-now` nightly with `X-Cron-Secret`.

---

## Notes

- Groq's free tier is a shared 200k tokens/day across your whole org and
  8k tokens/minute — a full run is ~40–150k tokens, so the pipeline is built
  to fail soft (validator fails open, evaluator ships degraded rather than
  looping, empty briefings raise rather than persist).
- `PROJECT_STATE.md` and `learning.md` are longer internal notes (gitignored
  by default).
