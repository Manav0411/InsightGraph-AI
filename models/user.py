"""
User profile and preferences models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


DEFAULT_PREFERRED_TOPICS = [
    "AI Agents & Agentic Workflows",
    "Large Language Models (LLMs)",
    "Foundation Model Releases",
    "LLM Infrastructure & Serving",
    "Open Source AI",
    "RAG & Vector Databases",
    "AI Alignment & Safety",
    "LLMOps & MLOps",
    "Multimodal AI",
    "AI Regulation & Policy",
    "AI Hardware & Chips",
    "AI Coding Assistants",
    "Prompt Engineering & Evals",
    "AI Startups & Funding",
    "AI Reasoning & Planning"
]

DEFAULT_EXCLUDED_TOPICS = [
    "Crypto & Blockchain",
    "NFTs",
    "Gaming",
    "Social Media Drama",
    "Sports"
]

class UserPreferences(BaseModel):
    """
    User interests and topic preferences for personalization.
    """

    preferred_topics: List[str] = Field(default_factory=lambda: DEFAULT_PREFERRED_TOPICS.copy())
    preferred_sources: List[str] = Field(default_factory=list)
    excluded_topics: List[str] = Field(default_factory=lambda: DEFAULT_EXCLUDED_TOPICS.copy())


class UserProfile(BaseModel):
    """
    Represents a full user profile.
    """

    user_id: str
    email: Optional[str] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
