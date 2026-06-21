import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.services.workflow_service import generate_autonomous_briefing
from backend.db.database import SessionLocal
from backend.models.db_user import User
from utils.logger import get_logger

logger = get_logger("scheduler")

async def daily_intelligence_generation():
    """
    Scheduled job that orchestrates intelligence generation for all users.
    """
    logger.info("[scheduler] Starting scheduled daily intelligence generation.")
    
    users = []
    with SessionLocal() as db:
        users = db.query(User).all()
        
    if not users:
        logger.warning("[scheduler] No users found for daily generation.")
    
    try:
        for user in users:
            try:
                await generate_autonomous_briefing(user.id)
            except Exception as e:
                logger.error(f"[scheduler] Failed autonomous generation for user {user.id}: {e}")
                
        logger.info("[scheduler] Completed scheduled daily intelligence generation.")
    except Exception as e:
        logger.error(f"[scheduler] Fatal error in daily generation job: {e}")

def start_scheduler(app):
    """
    Initializes the APScheduler and registers background tasks.
    Enforces a singleton pattern on the FastAPI app state to avoid duplicates during reloads.
    """
    if getattr(app.state, "scheduler_started", False):
        logger.info("[scheduler] Scheduler already running. Skipping initialization.")
        return

    logger.info("[scheduler] Initializing APScheduler...")
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        daily_intelligence_generation,
        trigger=CronTrigger(hour=8, minute=0),
        id="daily_intelligence_generation",
        name="Generate daily autonomous briefing",
        replace_existing=True,
        misfire_grace_time=3600,                                                  
    )
    
    scheduler.start()
    app.state.scheduler_started = True
    app.state.scheduler = scheduler
    logger.info("[scheduler] APScheduler started successfully. Jobs registered.")
