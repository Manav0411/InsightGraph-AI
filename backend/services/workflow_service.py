import time
import logging
from utils.user_loader import load_user_profile
from models.state import PipelineState
from graphs.newsletter_graph import create_newsletter_graph
from backend.schemas.responses import NewsletterResponse

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
    
    logger.info(f"[API] Returning newsletter response for user: {user_id}")
    
    return NewsletterResponse(
        message="Newsletter generated successfully",
        newsletter_content=state_obj.final_newsletter or "Failed to generate newsletter.",
        execution_time_seconds=execution_time,
        token_usage=token_usage,
        timings=metadata.agent_timings,
        metrics=metrics
    )
