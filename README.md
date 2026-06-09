# InsightGraph

An autonomous AI intelligence platform that aggregates, analyzes, and delivers highly personalized tech ecosystem insights. 

Instead of endless doomscrolling, InsightGraph uses an agentic pipeline to fetch daily signals from across the internet, analyze them for relevance based on your preferences, and present them in a clean, unified briefing.

##  Features

- **Autonomous Agentic Pipeline:** Built on LangGraph, the pipeline fetches data from Hacker News, ArXiv, and RSS feeds, then uses Groq (Llama 3) to filter, rank, and synthesize the signals.
- **Set & Forget Reader:** A clean, distraction-free consumer reading experience that automatically synthesizes your daily briefing in the background.
- **Long-Term Memory:** Uses `pgvector` and `SentenceTransformers` to store embeddings of all past articles, allowing the AI to generate longitudinal insights ("Why It Matters") by comparing new news with historical context.
- **Admin Command Center:** A secure `/admin` zone for power users to view real-time pipeline orchestration telemetry and Signal Quality Index (SQI) analytics.

##  Tech Stack

- **Frontend:** Next.js (App Router), TailwindCSS, Clerk Auth
- **Backend:** FastAPI, PostgreSQL (Neon + `pgvector`), SQLAlchemy
- **AI/Orchestration:** LangGraph, Groq, LangSmith

##  Quickstart

### 1. Backend Setup

Navigate to the root directory and install Python dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```env
# Required API Keys
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key

# PostgreSQL Connection
DATABASE_URL=postgresql://user:password@hostname/dbname

# Optional: LangSmith Observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=InsightGraph
```

Run the FastAPI server:
```bash
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup

Navigate to the frontend directory:
```bash
cd frontend
npm install
```

Create a `.env.local` file in the `frontend` directory:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL=/
NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL=/onboarding
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

