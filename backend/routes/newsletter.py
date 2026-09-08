from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Header
from sqlalchemy.orm import Session
from backend.schemas.requests import NewsletterRequest
from backend.schemas.responses import NewsletterResponse
from backend.services.workflow_service import run_newsletter_workflow
from backend.db.database import get_db, SessionLocal
from backend.services.persistence_service import save_briefing, fetch_latest_briefing, fetch_briefing_history_filtered, fetch_briefing_with_articles
from backend.dependencies.auth import get_current_user
from backend.services.task_manager import create_task, get_task_status, mark_task_completed, mark_task_failed
import os

def verify_generation_access(db: Session, user_id: str):
    from backend.models.db_user import User
    from backend.models.db_briefing import Briefing
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    admin_emails = [e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()]
    is_admin = user.email and user.email.lower() in admin_emails
    
    if not is_admin:
        briefing_count = db.query(Briefing).filter(Briefing.user_id == user_id).count()
        if briefing_count >= 1:
            raise HTTPException(status_code=403, detail="Non-admin users can only manually generate their first onboarding briefing. Further briefings are scheduled automatically.")

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])

from backend.services.persistence_service import get_user_profile_pydantic
import logging
logger = logging.getLogger("api_routes")

async def background_generation_task(request: NewsletterRequest, user_id: str, task_id: str):
    """Executes the newsletter workflow in the background and saves to DB."""
    try:
        with SessionLocal() as db:
            user_profile = get_user_profile_pydantic(db, user_id)
            
        response = await run_newsletter_workflow(request, user_profile, task_id=task_id)
        
        with SessionLocal() as db:
            save_briefing(db, user_id, response)
            
        mark_task_completed(task_id, result="success")
    except Exception as e:
        logger.error(f"Background task failed: {e}")
        mark_task_failed(task_id, str(e))

@router.post("/generate-async")
async def generate_newsletter_async(background_tasks: BackgroundTasks, request: NewsletterRequest, user_id: str = Depends(get_current_user)):
    """
    Spawns a background task to generate the newsletter. 
    Returns immediately with a task_id that the frontend can poll.
    """
    with SessionLocal() as db:
        verify_generation_access(db, user_id)
        
    task_id = create_task()
    background_tasks.add_task(background_generation_task, request, user_id, task_id)
    return {"task_id": task_id, "status": "accepted"}

@router.get("/status/{task_id}")
async def get_generation_status(task_id: str, user_id: str = Depends(get_current_user)):
    """
    Returns the real-time status of a background generation task.
    """
    status = get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@router.post("/generate", response_model=NewsletterResponse)
async def generate_newsletter(request: NewsletterRequest, user_id: str = Depends(get_current_user)):
    """
    Triggers the LangGraph orchestration to generate a personalized newsletter.
    This is a long-running synchronous task.
    """
    try:
        request.user_id = user_id
        
        with SessionLocal() as db:
            verify_generation_access(db, user_id)
            user_profile = get_user_profile_pydantic(db, user_id)
        
        response = await run_newsletter_workflow(request, user_profile)
        
        with SessionLocal() as db:
            save_briefing(db, user_id, response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.get("/latest")
async def get_latest_newsletter(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    """
    Returns the most recently generated newsletter from the PostgreSQL database.
    """
    from backend.services.persistence_service import fetch_latest_briefing
    briefing = fetch_latest_briefing(db, user_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="No newsletters have been generated yet.")
        
    articles_data = []
    for a in briefing.articles:
        articles_data.append({
            "title": a.title,
            "url": a.url,
            "image_url": a.image_url,
            "summary": a.summary,
            "details": a.details,
            "why_it_matters": a.why_it_matters,
            "source": a.source,
            "tags": a.tags,
            "trend_score": a.trend_score,
            "recommendation_reasons": [a.recommendation_reason] if a.recommendation_reason else [],
            "grounding_verified": a.is_grounded
        })
        
    return {
        "briefing": {
            "title": briefing.title
        },
        "articles": articles_data
    }

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
            "avg_trend_score": b.avg_trend_score,
            "execution_time_seconds": b.execution_time_seconds,
            "personalization_strength": b.personalization_strength,
            "matched_topics": b.matched_topics
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

@router.post("/generate-autonomous/{user_id}", response_model=NewsletterResponse)
async def generate_autonomous(user_id: str, x_cron_secret: str = Header(None)):
    """
    Server-to-server cron trigger. Accepts ZERO preferences in the payload,
    purely DB-driven orchestration. Secured via the X-Cron-Secret header.
    """
    expected_secret = os.getenv("CRON_SECRET")
    if not expected_secret:
        raise HTTPException(status_code=500, detail="CRON_SECRET is not configured on the server.")
    if x_cron_secret != expected_secret:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Cron Secret.")

    try:
        request = NewsletterRequest(user_id=user_id)
        
        with SessionLocal() as db:
            user_profile = get_user_profile_pydantic(db, user_id)
            
        response = await run_newsletter_workflow(request, user_profile)
        
        with SessionLocal() as db:
            save_briefing(db, user_id, response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autonomous workflow execution failed: {str(e)}")
