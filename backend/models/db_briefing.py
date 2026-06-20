import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.base import Base

class Briefing(Base):
    __tablename__ = "briefings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False, default="InsightGraph Digest")
    generated_at = Column(DateTime, default=datetime.utcnow)
    execution_time_seconds = Column(Float, default=0.0)
    
    workflow_health = Column(String, nullable=True)                                       
    grounding_reliability = Column(Float, default=100.0)
    validation_success_rate = Column(Float, default=100.0)
    
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    
    avg_trend_score = Column(Float, default=0.0)
    total_articles = Column(Integer, default=0)
    
    dominant_topics = Column(JSONB, default=list)
    top_signal = Column(JSONB, nullable=True)
    top_sources = Column(JSONB, default=list)
    signal_quality_index = Column(Float, default=0.0)
    
    matched_topics = Column(JSONB, default=list)
    matched_sources = Column(JSONB, default=list)
    personalization_strength = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="briefings")
    articles = relationship("Article", back_populates="briefing", cascade="all, delete-orphan")
