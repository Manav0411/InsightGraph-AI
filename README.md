# InsightGraph

An autonomous artificial intelligence platform designed to aggregate, analyze & deliver personalized technology ecosystem insights.

InsightGraph utilizes an agentic orchestration pipeline to retrieve daily signals from diverse web sources, evaluate their relevance against user-defined profiles & present the synthesized intelligence in a unified, structured briefing format.

## System Architecture and Features

- **Autonomous Agentic Pipeline:** Orchestrated via LangGraph, the data ingestion pipeline aggregates content from developer platforms, academic repositories & RSS feeds. It leverages large language models (via Groq) to filter, rank & synthesize incoming data streams.
- **Automated Intelligence Digests:** A streamlined consumption interface that processes daily briefings autonomously without manual intervention.
- **Longitudinal Memory Retrieval:** Implements vector search through PostgreSQL (`pgvector`) to index historical articles. This enables the analytical models to generate contextual insights by comparing emerging trends with foundational historical data.
- **Administrative Command Center:** A secure interface providing operational oversight, real-time pipeline telemetry, and Signal Quality Index (SQI) analytics.

## Technology Stack

- **Frontend Application:** Next.js (App Router), TailwindCSS, Clerk Authentication
- **Backend Infrastructure:** FastAPI, PostgreSQL (Neon Serverless with `pgvector`), SQLAlchemy ORM
- **Artificial Intelligence Orchestration:** LangGraph, Groq Inference API, LangSmith Observability
- **Deployment and Scheduling:** Vercel (Frontend), Render (Backend), GitHub Actions (Cron Scheduling)

## Project Structure

```text
ai_trend_intelligence/
├── backend/
│   ├── agents/          # LangGraph agents (analyzer, evaluator, composer)
│   ├── config/          # Centralized settings and constants
│   ├── db/              # SQLAlchemy database configuration
│   ├── models/          # Pydantic and SQLAlchemy models
│   ├── prompts/         # Decoupled LLM system prompts
│   ├── routes/          # FastAPI HTTP endpoints
│   ├── services/        # Core business logic (retrievers, vector store, persistence)
│   └── main.py          # FastAPI application entry point
├── frontend/
│   ├── public/          # Static assets
│   ├── src/
│   │   ├── app/         # Next.js App Router pages and layouts
│   │   ├── components/  # Reusable React components (UI, Theme, Clerk)
│   │   ├── context/     # React Context providers
│   │   └── lib/         # Utility functions and API clients
│   ├── package.json     # Node dependencies
│   └── tailwind.config.js # TailwindCSS configuration
├── utils/               # Shared utilities (logger, content cleaner)
├── .github/
│   └── workflows/       # GitHub Actions for CI/CD and cron scheduling
├── learning.md          # Project knowledge and architecture repository
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Local Development Configuration

### 1. Backend Service Initialization

Navigate to the project root directory and install the required Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory and populate it with the necessary credentials:

```env
# Required API Keys
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key
RESEND_API_KEY=your_key

# PostgreSQL Connection String
DATABASE_URL=postgresql://user:password@hostname/dbname

# Optional: LangSmith Observability Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=InsightGraph
```

Execute the FastAPI ASGI server:

```bash
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Application Initialization

Navigate to the frontend directory and install Node dependencies:

```bash
cd frontend
npm install
```

Create a `.env.local` file within the `frontend` directory:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL=/
NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL=/onboarding
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the Next.js development server:

```bash
npm run dev
```

### 3. Production Deployment

For production deployments, the frontend should be hosted on a Vercel edge network and the backend deployed as a Web Service on Render. Ensure that `NEXT_PUBLIC_API_URL` is updated to reflect the Render production URL, and that Clerk webhook endpoints are correctly configured to point to `/webhooks/clerk` on the live backend instance. Automatic scheduling can be configured via GitHub Actions.
