from fastapi import APIRouter, HTTPException, Depends
import asyncio
import json
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.schemas.requests import NewsletterRequest
from backend.schemas.responses import NewsletterResponse
from backend.services.workflow_service import run_newsletter_workflow
from backend.db.database import get_db
from backend.services.persistence_service import save_briefing, fetch_latest_briefing, fetch_briefing_history_filtered, fetch_briefing_with_articles
from backend.dependencies.auth import get_current_user
from utils.runtime_store import load_last_newsletter

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])

@router.post("/generate", response_model=NewsletterResponse)
async def generate_newsletter(request: NewsletterRequest, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    """
    Triggers the LangGraph orchestration to generate a personalized newsletter.
    This is a long-running synchronous task.
    """
    try:
        # Override the request user_id with the securely verified token user_id
        request.user_id = user_id
        response = await run_newsletter_workflow(request, db)
        # Persist to PostgreSQL alongside JSON cache
        save_briefing(db, user_id, response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.get("/latest", response_model=NewsletterResponse)
async def get_latest_newsletter(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    """
    Returns the most recently generated newsletter from the runtime store.
    Currently falls back to JSON cache.
    """
    data = load_last_newsletter()
    if not data:
        raise HTTPException(status_code=404, detail="No newsletters have been generated yet.")
    return data

@router.get("/history")
async def get_newsletter_history(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns the history of briefings from PostgreSQL with full metadata.
    """
    history = fetch_briefing_history_filtered(db, user_id)
    return [
        {
            "id": b.id,
            "title": b.title,
            "generated_at": b.generated_at,
            "total_articles": b.total_articles,
            "grounding_reliability": b.grounding_reliability,
            "dominant_topics": b.dominant_topics,
            "top_signal": b.top_signal,
            "signal_quality_index": b.signal_quality_index,
            "avg_trend_score": b.avg_trend_score
        }
        for b in history
    ]

@router.get("/history/{briefing_id}")
async def get_historical_briefing(briefing_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    """
    Returns a fully hydrated historical briefing with all its articles and context.
    """
    briefing = fetch_briefing_with_articles(db, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    
    # Optional: Verify that this briefing belongs to user_id
    if briefing.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this briefing")
        
    return {
        "id": briefing.id,
        "title": briefing.title,
        "generated_at": briefing.generated_at,
        "execution_time_seconds": briefing.execution_time_seconds,
        "tokens": {
            "prompt": briefing.prompt_tokens,
            "completion": briefing.completion_tokens
        },
        "metrics": {
            "grounding_reliability": briefing.grounding_reliability,
            "validation_success_rate": briefing.validation_success_rate,
            "signal_quality_index": briefing.signal_quality_index
        },
        "metadata": {
            "dominant_topics": briefing.dominant_topics,
            "top_signal": briefing.top_signal,
            "top_sources": briefing.top_sources
        },
        "articles": [
            {
                "title": a.title,
                "source": a.source,
                "url": a.url,
                "image_url": a.image_url,
                "summary": a.summary,
                "details": a.details,
                "why_it_matters": a.why_it_matters,
                "trend_score": a.trend_score,
                "tags": a.tags,
                "recommendation_reason": a.recommendation_reason,
                "is_grounded": a.is_grounded
            } for a in briefing.articles
        ]
    }

@router.get("/export/{briefing_id}")
async def export_briefing(briefing_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    """
    Generates a premium editorial markdown export of a historical briefing.
    """
    briefing = fetch_briefing_with_articles(db, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
        
    if briefing.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this briefing")
        
    md = f"# {briefing.title}\\n\\n"
    md += f"*Generated: {briefing.generated_at.strftime('%B %d, %Y')} | Signal Quality: {briefing.signal_quality_index}/100*\\n\\n"
    md += "---\\n\\n"
    
    for a in briefing.articles:
        md += f"## [{a.title}]({a.url})\\n"
        md += f"**Source:** {a.source} | **Trend Score:** {a.trend_score}\\n\\n"
        if a.tags:
            md += f"*{', '.join(a.tags)}*\\n\\n"
        md += f"{a.summary}\\n\\n"
        if a.why_it_matters:
            md += f"> **Why It Matters:** {a.why_it_matters}\\n\\n"
            
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(md, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename=InsightGraph_{briefing_id}.md"})

@router.post("/generate-stream")
async def generate_newsletter_stream(request: NewsletterRequest, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    """
    Simulates a live workflow execution panel by streaming progress updates via SSE,
    followed by the actual generation.
    """
    # Secure override
    request.user_id = user_id
    
    async def event_generator():
        stages = [
            ("Retrieving sources", 2.5),
            ("Validating articles", 1.0),
            ("Ranking intelligence", 0.5),
            ("Analyzing trends", 4.0),
            ("Evaluating summaries", 1.5),
            ("Composing digest", 1.0)
        ]
        for stage, delay in stages:
            yield f"data: {{\"stage\": \"{stage}\", \"status\": \"started\"}}\\n\\n"
            await asyncio.sleep(delay)
            yield f"data: {{\"stage\": \"{stage}\", \"status\": \"completed\"}}\\n\\n"
            
        yield f"data: {{\"stage\": \"Finalizing\", \"status\": \"started\"}}\\n\\n"
        
        try:
            # Run the actual workflow at the end to generate the final artifact
            response = await run_newsletter_workflow(request, db)
            
            # Persist to PostgreSQL alongside JSON cache
            save_briefing(db, user_id, response)
            
            yield f"data: {{\"stage\": \"Done\", \"status\": \"completed\", \"result\": \"success\"}}\\n\\n"
        except Exception as e:
            error_payload = json.dumps({"stage": "Error", "status": "failed", "error": str(e)})
            yield f"data: {error_payload}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/generate-autonomous/{user_id}", response_model=NewsletterResponse)
async def generate_autonomous(user_id: str, db: Session = Depends(get_db)):
    """
    Simulates a background cron trigger. 
    Accepts ZERO preferences in the payload, purely DB-driven orchestration.
    (Kept unauthenticated because it simulates a server-to-server or local webhook call).
    """
    try:
        request = NewsletterRequest(user_id=user_id)
        response = await run_newsletter_workflow(request, db)
        save_briefing(db, user_id, response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autonomous workflow execution failed: {str(e)}")
