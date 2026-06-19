from fastapi import APIRouter, Header, HTTPException
from backend.services.scheduler_service import daily_intelligence_generation
import os

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

@router.post("/run-now")
async def run_scheduler_now(x_cron_secret: str = Header(None)):
    """
    Manually triggers the daily intelligence generation job synchronously.
    Secured via X-Cron-Secret header for production cron triggering.
    """
    expected_secret = os.getenv("CRON_SECRET")
    if not expected_secret:
        raise HTTPException(status_code=500, detail="CRON_SECRET is not configured on the server.")
        
    if x_cron_secret != expected_secret:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Cron Secret.")
        
    await daily_intelligence_generation()
    return {"message": "Autonomous generation completed successfully."}
