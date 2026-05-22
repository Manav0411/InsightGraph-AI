from fastapi import APIRouter
from backend.schemas.responses import MetricsResponse
from utils.runtime_store import load_last_run

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("", response_model=MetricsResponse)
async def get_metrics():
    """
    Retrieves system-level execution telemetry from the latest run.
    """
    data = load_last_run()
    if data and "metrics" in data:
        m = data["metrics"]
        t = data.get("token_usage", {})
        return MetricsResponse(
            total_prompt_tokens=t.get("prompt_tokens", 0),
            total_completion_tokens=t.get("completion_tokens", 0),
            recovery_attempts=m.get("recovery_attempts", 0),
            conditional_routes_triggered=m.get("conditional_routes_triggered", 0),
            validation_failures=m.get("validation_failures", 0),
            grounding_rejections=m.get("grounding_rejections", 0),
            personalization_boosts_applied=m.get("personalization_boosts_applied", 0),
            total_articles_processed=m.get("total_articles_processed", 0),
            total_articles_rejected=m.get("total_articles_rejected", 0)
        )
    
    return MetricsResponse(
        total_prompt_tokens=0,
        total_completion_tokens=0,
        recovery_attempts=0,
        conditional_routes_triggered=0,
        validation_failures=0,
        grounding_rejections=0,
        personalization_boosts_applied=0,
        total_articles_processed=0,
        total_articles_rejected=0
    )
