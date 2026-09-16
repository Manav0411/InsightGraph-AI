from fastapi import APIRouter, HTTPException, Header
from backend.schemas.requests import UserPreferencesUpdate
from backend.schemas.responses import UserResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from backend.db.database import get_db
from backend.services.persistence_service import get_user_profile_pydantic, update_user_preferences
from backend.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    """
    Retrieves the user profile and preferences.

    This is typically the first authenticated call a brand-new user makes, and
    it usually wins the race against Clerk's `user.created` webhook (the other
    place a user row gets created — see routes/webhooks.py). The frontend
    already knows the signed-in user's email at this point, so it sends it via
    `X-User-Email`; passing it through here means the row gets the right email
    at creation instead of sitting blank until (or unless) the webhook catches up.
    """
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    profile = get_user_profile_pydantic(db, user_id, email=x_user_email)
    return UserResponse(profile=profile)

@router.post("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, request: UserPreferencesUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Updates the user's personalization preferences directly in PostgreSQL.
    """
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    profile = update_user_preferences(db, user_id, request)
    return UserResponse(profile=profile)
