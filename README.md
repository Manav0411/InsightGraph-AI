# InsightGraph
> Adaptive AI Intelligence Platform

InsightGraph is a highly automated, production-ready AI intelligence pipeline that autonomously fetches, filters, and synthesizes the latest developments in Artificial Intelligence into personalized digests.

## Features
- **Adaptive Orchestration:** Built on **LangGraph**, featuring dynamic routing, cyclic loops for error recovery, and robust execution state management.
- **Source-Aware Intelligence:** Aggregates and intelligently parses both AI news (via Tavily) and trending open-source repositories (via GitHub API).
- **FastAPI Backend:** Exposes the entire pipeline securely through a REST API, providing robust endpoints for triggering generations and updating user preferences.
- **Grounding & Validation:** Deterministic filtering agents prevent LLM hallucinations by enforcing strict keyword overlaps between source headlines and generated summaries.
- **Full Observability:** Instrumentated with **LangSmith** to monitor LLM token usage, tracing, and agent telemetry.

## Quickstart

### 1. Set Environment Variables
Create a `.env` file in the root directory:
```env
TAVILY_API_KEY=your_key
GROQ_API_KEY=your_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=InsightGraph
```

### 2. Run the API Server
```bash
source venv/bin/activate
uvicorn backend.main:app --reload
```
Navigate to `http://127.0.0.1:8000/docs` to interact with the API Swagger UI.

### 3. Generate Intelligence
You can test the pipeline locally without the API by running:
```bash
python run_pipeline.py
```
This will generate the latest AI digest inside the `output/` directory.
