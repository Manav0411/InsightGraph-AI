import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.base import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    briefing_id = Column(String, ForeignKey("briefings.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    
    summary = Column(Text, nullable=True)
    details = Column(JSONB, default=list)
    why_it_matters = Column(Text, nullable=True)
    
    trend_score = Column(Float, default=0.0)
    confidence_score = Column(Float, nullable=True)
    
    tags = Column(JSONB, default=list)
    recommendation_reason = Column(Text, nullable=True)
    is_grounded = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    briefing = relationship("Briefing", back_populates="articles")
