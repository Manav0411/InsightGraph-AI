from fastapi import APIRouter
from backend.schemas.responses import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("", response_model=MetricsResponse)
async def get_metrics():
    """
    Retrieves system-level execution telemetry.
    Note: Currently returns mocked/default values as we don't have a persistent metrics database yet.
    """
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
