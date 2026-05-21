from pydantic import BaseModel
from typing import List, Optional, Dict
from models.user import UserProfile

class NewsletterResponse(BaseModel):
    message: str
    newsletter_content: str
    execution_time_seconds: float
    token_usage: Dict[str, int]
    timings: Dict[str, float]
    metrics: Dict[str, int]

class UserResponse(BaseModel):
    profile: UserProfile

class MetricsResponse(BaseModel):
    total_prompt_tokens: int
    total_completion_tokens: int
    recovery_attempts: int
    conditional_routes_triggered: int
    validation_failures: int
    grounding_rejections: int
    personalization_boosts_applied: int
    total_articles_processed: int
    total_articles_rejected: int
