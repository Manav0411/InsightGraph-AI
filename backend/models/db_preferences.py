import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.base import Base
from models.user import DEFAULT_PREFERRED_TOPICS, DEFAULT_EXCLUDED_TOPICS

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    preferred_topics = Column(JSONB, default=lambda: DEFAULT_PREFERRED_TOPICS.copy())
    excluded_topics = Column(JSONB, default=lambda: DEFAULT_EXCLUDED_TOPICS.copy())
    trusted_sources = Column(JSONB, default=list)
    behavioral_tuning = Column(JSONB, default=dict)
    email_delivery_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="preferences")
