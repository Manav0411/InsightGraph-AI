import time
import logging
from backend.services.persistence_service import get_user_profile_pydantic
from sqlalchemy.orm import Session
from models.state import PipelineState
from graphs.newsletter_graph import create_newsletter_graph
from backend.schemas.responses import NewsletterResponse, ArticleResponse, TrustMetrics
from utils.runtime_store import save_last_run

from backend.schemas.requests import NewsletterRequest

logger = logging.getLogger("api_workflow")

async def run_newsletter_workflow(request: NewsletterRequest, user_profile, task_id: str = None) -> NewsletterResponse:
    """
    Wraps the LangGraph orchestration.
    Runs the pipeline synchronously since LangGraph execution blocks,
    but provides an async interface for the FastAPI route.
    """
    user_id = request.user_id
    logger.info(f"[API] Newsletter generation requested for user: {user_id}")
    
    
    initial_state = PipelineState(
        user_profile=user_profile
    )
    
    graph = create_newsletter_graph()
    
    start_time = time.perf_counter()
    
    if task_id:
        from backend.services.task_manager import update_task_stage
        final_state = None
        async for state_value in graph.astream(initial_state, stream_mode="values"):
            stage = state_value.get("pipeline_stage", "Initializing...")
            update_task_stage(task_id, f"Running: {stage}")
            final_state = state_value
    else:
        final_state = await graph.ainvoke(initial_state)
        
    end_time = time.perf_counter()
    
    execution_time = round(end_time - start_time, 2)
    
    state_obj = PipelineState(**final_state)
    metadata = state_obj.metadata

    if not state_obj.articles:
        error_detail = "; ".join(state_obj.errors) if state_obj.errors else "unknown cause"
        logger.error(f"[API] Pipeline for user {user_id} produced 0 valid articles ({error_detail}). Not persisting an empty briefing.")
        raise RuntimeError(f"Pipeline produced no valid articles ({error_detail})")

    metrics = {
        "recovery_attempts": metadata.recovery_attempts,
        "conditional_routes_triggered": metadata.conditional_routes_triggered,
        "validation_failures": metadata.validation_failures,
        "grounding_rejections": metadata.grounding_rejections,
        "personalization_boosts_applied": metadata.personalization_boosts_applied,
        "total_articles_processed": metadata.total_articles_processed,
        "total_articles_rejected": metadata.total_articles_rejected
    }
    
    token_usage = {
        "prompt_tokens": metadata.total_prompt_tokens,
        "completion_tokens": metadata.total_completion_tokens
    }
    
    total_processed = metadata.total_articles_processed
    if total_processed > 0:
        val_success = ((total_processed - metadata.validation_failures) / total_processed) * 100
        grounding_pct = ((total_processed - metadata.grounding_rejections) / total_processed) * 100
    else:
        val_success = 100.0
        grounding_pct = 100.0

    trust_metrics = {
        "grounding_reliability_pct": round(grounding_pct, 1),
        "validation_success_rate": round(val_success, 1),
        "source_diversity_healthy": len(metadata.retrieval_sources) > 1,
        "hallucination_rejections": metadata.grounding_rejections,
        "total_signals_processed": total_processed
    }

    all_articles = []
    for a in state_obj.articles:
        all_articles.append(ArticleResponse(
            title=a.title,
            url=a.url,
            image_url=a.image_url,
            summary=a.summary or "",
            details=a.details or [],
            why_it_matters=a.why_it_matters or "",
            source=a.source,
            tags=a.tags,
            trend_score=a.trend_score,
            personalization_boost=a.personalization_boost,
            stars=a.stars,
            recommendation_reasons=a.recommendation_reasons,
            grounding_verified=a.grounding_verified
        ))
        
    recommended_articles = [a for a in all_articles if a.personalization_boost > 0][:2]
    
    logger.info(f"[API] Returning newsletter response for user: {user_id}")
    
    response = NewsletterResponse(
        message="Newsletter generated successfully",
        newsletter_content=state_obj.final_newsletter or "Failed to generate newsletter.",
        articles=all_articles,
        recommended_articles=recommended_articles,
        execution_time_seconds=execution_time,
        token_usage=token_usage,
        timings=metadata.agent_timings,
        metrics=metrics,
        trust_metrics=TrustMetrics(**trust_metrics)
    )
    
    save_last_run(response.model_dump())
    
    return response

async def generate_autonomous_briefing(user_id: str):
    """
    Per-user background trigger for the daily pipeline (invoked by
    daily_intelligence_generation). Creates its own DB session so it doesn't
    depend on FastAPI request cycles.
    """
    from backend.db.database import SessionLocal
    from backend.services.persistence_service import save_briefing
    
    logger.info(f"[scheduler] Initiating autonomous briefing generation for user: {user_id}")
    try:
        from backend.models.db_user import User
        from backend.services.email_service import send_briefing_email
        
        request = NewsletterRequest(user_id=user_id)
        
        with SessionLocal() as db:
            user_profile = get_user_profile_pydantic(db, user_id)
            
        response = await run_newsletter_workflow(request, user_profile)
        
        with SessionLocal() as db:
            db_briefing = save_briefing(db, user_id, response)
            user = db.query(User).filter(User.id == user_id).first()
            if user and db_briefing:
                if user.preferences and getattr(user.preferences, 'email_delivery_enabled', True):
                    await send_briefing_email(db, user, db_briefing)
                else:
                    logger.info(f"[scheduler] Email delivery disabled for user {user_id}. Skipping email.")

        logger.info(f"[scheduler] Successfully completed autonomous generation for {user_id}")
        return response
    except Exception as e:
        logger.error(f"[scheduler] Autonomous workflow failed for user {user_id}: {str(e)}")
        raise
