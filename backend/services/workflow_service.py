import time
import logging
from utils.user_loader import load_user_profile
from models.state import PipelineState
from graphs.newsletter_graph import create_newsletter_graph
from backend.schemas.responses import NewsletterResponse, ArticleResponse, TrustMetrics
from utils.runtime_store import save_last_run

logger = logging.getLogger("api_workflow")

async def run_newsletter_workflow(user_id: str) -> NewsletterResponse:
    """
    Wraps the LangGraph orchestration.
    Runs the pipeline synchronously since LangGraph execution blocks,
    but provides an async interface for the FastAPI route.
    """
    logger.info(f"[API] Newsletter generation requested for user: {user_id}")
    
    # 1. Load User Profile
    user_profile = load_user_profile(user_id)
    
    # 2. Initialize State
    initial_state = PipelineState(
        user_profile=user_profile
    )
    
    # 3. Create and Run Graph
    graph = create_newsletter_graph()
    
    start_time = time.perf_counter()
    # Note: For fully async execution, we could use graph.ainvoke if all nodes were async.
    # Since our agents are synchronous, we'll use invoke.
    final_state = graph.invoke(initial_state)
    end_time = time.perf_counter()
    
    execution_time = round(end_time - start_time, 2)
    
    # 4. Extract data from final state
    state_obj = PipelineState(**final_state)
    metadata = state_obj.metadata
    
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
            summary=a.summary or "",
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
