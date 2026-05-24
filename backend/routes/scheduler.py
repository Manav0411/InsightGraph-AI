from fastapi import APIRouter
from backend.services.scheduler_service import daily_intelligence_generation

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

@router.post("/run-now")
async def run_scheduler_now():
    """
    Manually triggers the daily intelligence generation job synchronously for testing.
    """
    await daily_intelligence_generation()
    return {"message": "Autonomous generation completed successfully."}
