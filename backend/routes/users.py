from fastapi import APIRouter, HTTPException
from backend.schemas.requests import UserPreferencesUpdate
from backend.schemas.responses import UserResponse
from utils.user_loader import load_user_profile, save_user_profile

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Retrieves the user profile and preferences.
    """
    profile = load_user_profile(user_id)
    return UserResponse(profile=profile)

@router.post("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, request: UserPreferencesUpdate):
    """
    Updates the user's personalization preferences.
    """
    profile = load_user_profile(user_id)
    
    # Update fields if provided
    if request.preferred_topics is not None:
        profile.preferences.preferred_topics = request.preferred_topics
    if request.preferred_sources is not None:
        profile.preferences.preferred_sources = request.preferred_sources
    if request.excluded_topics is not None:
        profile.preferences.excluded_topics = request.excluded_topics
        
    save_user_profile(profile)
    
    return UserResponse(profile=profile)
