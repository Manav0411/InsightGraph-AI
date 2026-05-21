from fastapi import APIRouter, HTTPException
from backend.schemas.requests import NewsletterRequest
from backend.schemas.responses import NewsletterResponse
from backend.services.workflow_service import run_newsletter_workflow

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])

@router.post("/generate", response_model=NewsletterResponse)
async def generate_newsletter(request: NewsletterRequest):
    """
    Triggers the LangGraph orchestration to generate a personalized newsletter.
    This is a long-running synchronous task.
    """
    try:
        response = await run_newsletter_workflow(request.user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")
