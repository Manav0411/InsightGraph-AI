from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.services.persistence_service import fetch_longitudinal_analytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/trends")
async def get_analytics_trends(user_id: str = "default_user", db: Session = Depends(get_db)):
    """
    Returns longitudinal platform intelligence trends including tokens, latency, topics, and sources.
    """
    return fetch_longitudinal_analytics(db, user_id)
