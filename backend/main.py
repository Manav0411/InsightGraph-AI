from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

from backend.routes import newsletter, users, metrics, analytics, scheduler, email, webhooks
from backend.db.database import get_db, engine
from backend.db.base import Base
from utils.logger import get_logger

logger = get_logger("database")

app = FastAPI(
    title="InsightGraph API",
    description="Production backend for InsightGraph - the Adaptive AI Intelligence Platform.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(newsletter.router)
app.include_router(users.router)
app.include_router(metrics.router)
app.include_router(analytics.router)
app.include_router(scheduler.router)
app.include_router(email.router)
app.include_router(webhooks.router)

@app.get("/health", tags=["Health"])
async def health():
    """
    Basic health check route.
    """
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing application and verifying DB connectivity...")
    
    # Recover tasks
    from backend.services.task_manager import load_tasks, active_tasks, save_tasks
    load_tasks()
    recovered_count = 0
    for task_id, state in active_tasks.items():
        if state.get("status") == "running":
            state["status"] = "failed"
            state["stage"] = "Error"
            state["error"] = "Server restarted during generation"
            recovered_count += 1
    if recovered_count > 0:
        save_tasks()
        logger.info(f"Recovered and marked {recovered_count} in-flight tasks as failed.")
        
    try:
        # A lightweight connection test
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("PostgreSQL connectivity verified successfully on startup.")
        
        # Temporary auto-creation of tables (Before Alembic)
        # Import models here to register them with Base.metadata to avoid circular imports
        from backend.models.db_user import User
        from backend.models.db_preferences import UserPreferences
        from backend.models.db_briefing import Briefing
        from backend.models.db_article import Article
        from backend.models.db_email_log import EmailDeliveryLog
        
        Base.metadata.create_all(bind=engine)
        logger.info("SQLAlchemy metadata verified tables.")
        
        # Start Autonomous Scheduler
        from backend.services.scheduler_service import start_scheduler
        start_scheduler(app)
        
    except Exception as e:
        logger.error(f"PostgreSQL connectivity failed on startup: {e}")
        logger.warning("Application starting without DB functionality. Using fallback persistence if needed.")

@app.get("/db-health", tags=["Health"])
async def db_health(db: Session = Depends(get_db)):
    """
    Verifies PostgreSQL connectivity and SQLAlchemy session stability.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"database": "healthy"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"database": "unhealthy", "error": str(e)}
