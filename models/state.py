"""
Centralized pipeline state models.

Why this matters:
- Provides strict schema validation
- Makes LangGraph state management cleaner
- Prevents inconsistent payload structures
- Improves debugging and observability
- Makes frontend/API integration easier later

This file will become the single source of truth
for all agent communication in the pipeline.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Article(BaseModel):
    """
    Represents a single processed intelligence item.
    """

    title: str
    url: str

    # Original retrieved content
    content: str

    # Source information
    source: str

    # AI-generated fields
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None

    # Classification
    tags: List[str] = Field(default_factory=list)

    # Ranking
    trend_score: float = 0.0

    # GitHub-specific metadata
    stars: Optional[int] = None

    # Tracking metadata
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)


class PipelineMetadata(BaseModel):
    """
    Stores execution-level analytics and metrics.
    Useful later for:
    - dashboards
    - LangSmith traces
    - monitoring
    - analytics
    """

    total_articles_retrieved: int = 0
    total_articles_processed: int = 0
    total_articles_rejected: int = 0

    execution_time_seconds: float = 0.0

    retrieval_sources: List[str] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PipelineState(BaseModel):
    """
    Global pipeline state passed between agents.

    This structure will later become the LangGraph State object.
    """

    articles: List[Article] = Field(default_factory=list)

    metadata: PipelineMetadata = Field(
        default_factory=PipelineMetadata
    )
    
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    pipeline_stage: str = "initialized"
