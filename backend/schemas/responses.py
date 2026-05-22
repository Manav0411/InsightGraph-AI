from pydantic import BaseModel
from typing import List, Optional, Dict
from models.user import UserProfile

class TrustMetrics(BaseModel):
    grounding_reliability_pct: float
    validation_success_rate: float
    source_diversity_healthy: bool
    hallucination_rejections: int
    total_signals_processed: int

class ArticleResponse(BaseModel):
    title: str
    url: str
    summary: str
    why_it_matters: str
    source: str
    tags: List[str]
    trend_score: float
    personalization_boost: float
    stars: Optional[int] = None
    recommendation_reasons: List[str]
    grounding_verified: bool

class NewsletterResponse(BaseModel):
    message: str
    newsletter_content: str
    articles: List[ArticleResponse]
    recommended_articles: List[ArticleResponse]
    execution_time_seconds: float
    token_usage: Dict[str, int]
    timings: Dict[str, float]
    metrics: Dict[str, int]
    trust_metrics: TrustMetrics

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
