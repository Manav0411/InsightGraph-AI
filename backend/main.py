from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

from backend.routes import newsletter, users, metrics
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(newsletter.router)
app.include_router(users.router)
app.include_router(metrics.router)

@app.get("/health", tags=["Health"])
async def health():
    """
    Basic health check route.
    """
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing application and verifying DB connectivity...")
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
        
        Base.metadata.create_all(bind=engine)
        logger.info("SQLAlchemy metadata verified tables.")
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
