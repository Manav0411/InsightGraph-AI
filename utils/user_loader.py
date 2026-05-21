"""
Utility for loading user profiles from local JSON storage.
"""

import os
import json
import logging
from models.user import UserProfile, UserPreferences

logger = logging.getLogger(__name__)


def load_user_profile(user_id: str) -> UserProfile:
    """
    Load a user profile from data/users/{user_id}.json.
    Falls back to a default profile if not found or if parsing fails.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_path = os.path.join(base_dir, "data", "users", f"{user_id}.json")

    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded user profile for '{user_id}' from {profile_path}")
            return UserProfile(**data)
        except Exception as e:
            logger.error(f"Error loading user profile from {profile_path}: {e}. Falling back to default.")

    logger.warning(f"User profile file for '{user_id}' not found. Initializing fallback profile.")
    return UserProfile(
        user_id=user_id,
        preferences=UserPreferences(
            preferred_topics=["AI Agents", "Coding Assistants"],
            preferred_sources=["github"],
            excluded_topics=["Robotics"]
        )
    )
