import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.base import Base

class EmailDeliveryLog(Base):
    __tablename__ = "email_delivery_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    briefing_id = Column(String, ForeignKey("briefings.id", ondelete="CASCADE"), nullable=True)
    recipient_email = Column(String, nullable=False)
    
    status = Column(String, nullable=False)  # "success" or "failed"
    error_message = Column(Text, nullable=True)
    delivered_at = Column(DateTime, default=datetime.utcnow)
    
    # Advanced Telemetry
    provider_message_id = Column(String, nullable=True)
    delivery_type = Column(String, nullable=False, default="daily_digest")
    template_version = Column(String, nullable=False, default="v1.0")
    
    # Historical Rendering Traceability
    rendered_email_html = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", backref="email_logs")
    briefing = relationship("Briefing", backref="email_logs")
