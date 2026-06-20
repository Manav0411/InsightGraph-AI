import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.logger import get_logger

logger = get_logger("database")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is missing!")
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/insightgraph"

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,                                                 
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("PostgreSQL engine initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize PostgreSQL engine: {e}")
    raise

def get_db():
    """
    Dependency to yield a database session for FastAPI routes.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()
