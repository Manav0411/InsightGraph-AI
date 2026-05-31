from sqlalchemy.orm import Session
from sqlalchemy import desc
from collections import Counter
from backend.models.db_user import User
from backend.models.db_preferences import UserPreferences
from backend.models.db_briefing import Briefing
from backend.models.db_article import Article
from backend.schemas.requests import UserPreferencesUpdate
from backend.schemas.responses import NewsletterResponse
from models.user import UserProfile, UserPreferences as PydanticUserPreferences, DEFAULT_PREFERRED_TOPICS, DEFAULT_EXCLUDED_TOPICS
from utils.logger import get_logger

logger = get_logger("persistence")

def create_or_get_user(db: Session, user_id: str, email: str = None) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, email=email)
        db.add(user)
        prefs = UserPreferences(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(user)
        logger.info(f"[Persistence] Created new user profile for {user_id}")
    else:
        if email and user.email != email:
            user.email = email
            db.commit()
            logger.info(f"[Persistence] Updated email for user {user_id}")
    return user

def get_user_profile_pydantic(db: Session, user_id: str) -> UserProfile:
    """Loads user preferences from PostgreSQL and returns the Pydantic UserProfile expected by LangGraph."""
    db_user = create_or_get_user(db, user_id)
    db_prefs = db_user.preferences
    
    return UserProfile(
        user_id=user_id,
        preferences=PydanticUserPreferences(
            preferred_topics=db_prefs.preferred_topics if db_prefs.preferred_topics else DEFAULT_PREFERRED_TOPICS.copy(),
            preferred_sources=db_prefs.trusted_sources or [],
            excluded_topics=db_prefs.excluded_topics if db_prefs.excluded_topics else DEFAULT_EXCLUDED_TOPICS.copy()
        )
    )

def update_user_preferences(db: Session, user_id: str, request: UserPreferencesUpdate) -> UserProfile:
    """Updates user preferences in PostgreSQL."""
    db_user = create_or_get_user(db, user_id)
    db_prefs = db_user.preferences
    
    if request.preferred_topics is not None:
        db_prefs.preferred_topics = request.preferred_topics
    if request.preferred_sources is not None:
        db_prefs.trusted_sources = request.preferred_sources
    if request.excluded_topics is not None:
        db_prefs.excluded_topics = request.excluded_topics
        
    db.commit()
    return get_user_profile_pydantic(db, user_id)

def save_briefing(db: Session, user_id: str, response: NewsletterResponse) -> Briefing:
    create_or_get_user(db, user_id)
    trust_metrics = response.trust_metrics.model_dump() if response.trust_metrics else {}
    
    # Compute Denormalized Metadata
    all_tags = []
    sources = []
    top_article = None
    max_trend = -1
    
    # Extract personalization metadata from recommendation reasons
    matched_topics_set = set()
    matched_sources_set = set()
    total_boosts = 0
    
    for a in response.articles:
        all_tags.extend(a.tags)
        sources.append(a.source)
        
        # Parse recommendation reasons
        for reason in a.recommendation_reasons:
            if "Matches preferred topic:" in reason:
                topic = reason.split("Matches preferred topic:")[1].split("(")[0].strip()
                matched_topics_set.add(topic)
                total_boosts += 1
            elif "Preferred source:" in reason:
                source = reason.split("Preferred source:")[1].split("(")[0].strip()
                matched_sources_set.add(source)
                total_boosts += 1
                
        if a.trend_score > max_trend:
            max_trend = a.trend_score
            top_article = {"title": a.title, "url": a.url, "trend_score": a.trend_score}
            
    tag_counts = Counter(all_tags)
    dominant_topics = [tag for tag, count in tag_counts.most_common(5)]
    
    source_counts = Counter(sources)
    top_sources = [{"source": src, "count": count} for src, count in source_counts.most_common(5)]
    
    personalization_strength = min((total_boosts / max(len(response.articles), 1)) * 10, 100.0)
    
    grounding = trust_metrics.get("grounding_reliability_pct", 100.0)
    validation = trust_metrics.get("validation_success_rate", 100.0)
    avg_trend = sum(a.trend_score for a in response.articles) / max(len(response.articles), 1)
    
    normalized_trend = min(avg_trend * 5, 100.0)
    sqi = round((grounding * 0.4) + (validation * 0.3) + (normalized_trend * 0.3), 1)

    # Generate dynamic title
    if dominant_topics:
        top_two = dominant_topics[:2]
        title_suffix = " & ".join(top_two)
        dynamic_title = f"InsightGraph Digest: {title_suffix}"
    else:
        dynamic_title = "InsightGraph Digest"

    db_briefing = Briefing(
        user_id=user_id,
        title=dynamic_title,
        execution_time_seconds=response.execution_time_seconds,
        prompt_tokens=response.token_usage.get("prompt_tokens", 0),
        completion_tokens=response.token_usage.get("completion_tokens", 0),
        avg_trend_score=avg_trend,
        total_articles=len(response.articles),
        grounding_reliability=grounding,
        validation_success_rate=validation,
        workflow_health="success",
        dominant_topics=dominant_topics,
        top_signal=top_article,
        top_sources=top_sources,
        signal_quality_index=sqi,
        matched_topics=list(matched_topics_set),
        matched_sources=list(matched_sources_set),
        personalization_strength=round(personalization_strength, 1)
    )
    
    db.add(db_briefing)
    db.flush()
    
    for a in response.articles:
        db_article = Article(
            briefing_id=db_briefing.id,
            title=a.title,
            source=a.source,
            url=a.url,
            image_url=a.image_url,
            summary=a.summary,
            details=a.details,
            why_it_matters=a.why_it_matters,
            trend_score=a.trend_score,
            confidence_score=None,
            tags=a.tags,
            recommendation_reason=", ".join(a.recommendation_reasons) if a.recommendation_reasons else None,
            is_grounded=a.grounding_verified
        )
        db_briefing.articles.append(db_article)
        db.add(db_article)
        
    db.commit()
    db.refresh(db_briefing)
    logger.info(f"[Persistence] Saved briefing {db_briefing.id} with SQI {sqi}")
    
    # Ingest into Vector Memory
    try:
        from backend.services.vector_store import memory_manager
        memory_manager.store_briefing(db_briefing)
    except Exception as e:
        logger.error(f"[Persistence] Failed to index into Vector Memory: {e}")
        
    return db_briefing

def fetch_latest_briefing(db: Session, user_id: str):
    return db.query(Briefing).filter(Briefing.user_id == user_id).order_by(desc(Briefing.created_at)).first()

def fetch_briefing_history_filtered(db: Session, user_id: str, limit: int = 50):
    # Base filter implementation, extensible via kwargs
    return db.query(Briefing).filter(Briefing.user_id == user_id).order_by(desc(Briefing.created_at)).limit(limit).all()

def fetch_briefing_with_articles(db: Session, briefing_id: str):
    return db.query(Briefing).filter(Briefing.id == briefing_id).first()

def fetch_longitudinal_analytics(db: Session, user_id: str, limit: int = 20):
    briefings = db.query(Briefing).filter(Briefing.user_id == user_id).order_by(Briefing.created_at).limit(limit).all()
    
    token_trends = []
    latency_trends = []
    all_topics = []
    all_sources = []
    
    for b in briefings:
        date_str = b.created_at.isoformat() + "Z"
        token_trends.append({"date": date_str, "prompt": b.prompt_tokens, "completion": b.completion_tokens})
        latency_trends.append({"date": date_str, "latency": b.execution_time_seconds, "sqi": b.signal_quality_index})
        
        if b.dominant_topics:
            all_topics.extend(b.dominant_topics)
        if b.top_sources:
            for src in b.top_sources:
                all_sources.append(src["source"])
                
    topic_counts = Counter(all_topics)
    source_counts = Counter(all_sources)
    
    return {
        "token_trends": token_trends,
        "latency_trends": latency_trends,
        "fastest_growing_topics": [{"topic": k, "count": v} for k, v in topic_counts.most_common(5)],
        "source_distribution": [{"source": k, "count": v} for k, v in source_counts.most_common(5)]
    }
