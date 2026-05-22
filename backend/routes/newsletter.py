from fastapi import APIRouter, HTTPException
import asyncio
from fastapi.responses import StreamingResponse
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
        response = await run_newsletter_workflow(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

from utils.runtime_store import load_last_newsletter

@router.get("/latest", response_model=NewsletterResponse)
async def get_latest_newsletter():
    """
    Returns the most recently generated newsletter from the runtime store.
    """
    data = load_last_newsletter()
    if not data:
        raise HTTPException(status_code=404, detail="No newsletters have been generated yet.")
    return data

@router.post("/generate-stream")
async def generate_newsletter_stream(request: NewsletterRequest):
    """
    Simulates a live workflow execution panel by streaming progress updates via SSE,
    followed by the actual generation.
    """
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
            response = await run_newsletter_workflow(request)
            yield f"data: {{\"stage\": \"Done\", \"status\": \"completed\", \"result\": \"success\"}}\\n\\n"
        except Exception as e:
            yield f"data: {{\"stage\": \"Error\", \"status\": \"failed\", \"error\": \"{str(e)}\"}}\\n\\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
