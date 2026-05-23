from pydantic import BaseModel
from typing import List, Optional

class NewsletterRequest(BaseModel):
    user_id: str

class UserPreferencesUpdate(BaseModel):
    preferred_topics: Optional[List[str]] = None
    preferred_sources: Optional[List[str]] = None
    excluded_topics: Optional[List[str]] = None
