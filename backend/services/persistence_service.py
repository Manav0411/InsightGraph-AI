from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.db_user import User
from backend.models.db_preferences import UserPreferences
from backend.models.db_briefing import Briefing
from backend.models.db_article import Article
from backend.schemas.responses import NewsletterResponse, ArticleResponse, TrustMetrics
from utils.logger import get_logger

logger = get_logger("persistence")

def create_or_get_user(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id)
        db.add(user)
        # Add default preferences
        prefs = UserPreferences(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(user)
        logger.info(f"[Persistence] Created new user profile for {user_id}")
    return user

def save_briefing(db: Session, user_id: str, response: NewsletterResponse) -> Briefing:
    """
    Persists a generated NewsletterResponse into the database.
    This safely translates the Pydantic API response into our relational ORM structure.
    """
    create_or_get_user(db, user_id)
    
    trust_metrics = response.trust_metrics.model_dump() if response.trust_metrics else {}
    
    db_briefing = Briefing(
        user_id=user_id,
        title="InsightGraph Digest",
        execution_time_seconds=response.execution_time_seconds,
        prompt_tokens=response.token_usage.get("prompt_tokens", 0),
        completion_tokens=response.token_usage.get("completion_tokens", 0),
        avg_trend_score=sum(a.trend_score for a in response.articles) / max(len(response.articles), 1),
        total_articles=len(response.articles),
        grounding_reliability=trust_metrics.get("grounding_reliability_pct", 100.0),
        validation_success_rate=trust_metrics.get("validation_success_rate", 100.0),
        workflow_health="success"
    )
    
    db.add(db_briefing)
    db.flush() # Flush to get the briefing ID for articles
    
    for a in response.articles:
        db_article = Article(
            briefing_id=db_briefing.id,
            title=a.title,
            source=a.source,
            url=a.url,
            summary=a.summary,
            why_it_matters=a.why_it_matters,
            trend_score=a.trend_score,
            confidence_score=None,
            tags=a.tags,
            recommendation_reason=", ".join(a.recommendation_reasons) if a.recommendation_reasons else None,
            is_grounded=a.grounding_verified
        )
        db.add(db_article)
        
    db.commit()
    db.refresh(db_briefing)
    logger.info(f"[Persistence] Saved new briefing {db_briefing.id} for user {user_id} with {len(response.articles)} articles")
    return db_briefing

def fetch_latest_briefing(db: Session, user_id: str):
    """
    Fetches the most recent briefing for a user.
    """
    briefing = db.query(Briefing).filter(Briefing.user_id == user_id).order_by(desc(Briefing.created_at)).first()
    return briefing

def fetch_briefing_history(db: Session, user_id: str):
    """
    Fetches the history of briefings for a user.
    """
    briefings = db.query(Briefing).filter(Briefing.user_id == user_id).order_by(desc(Briefing.created_at)).all()
    return briefings
