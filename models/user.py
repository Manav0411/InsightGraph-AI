"""
User profile and preferences models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class UserPreferences(BaseModel):
    """
    User interests and topic preferences for personalization.
    """

    preferred_topics: List[str] = Field(default_factory=list)
    preferred_sources: List[str] = Field(default_factory=list)
    excluded_topics: List[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    """
    Represents a full user profile.
    """

    user_id: str
    email: Optional[str] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
