from fastapi import APIRouter, Depends, HTTPException
from ..schemas.user import UserProfile
from ..services.db_service import create_user_profile, get_user_by_netid, update_user_profile
from ..auth.dependencies import get_current_user
from ..models.db_models import UserProfileDB

router = APIRouter()

@router.post("/profile")
def create_profile(
    profile: UserProfile,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Create profile - uses authenticated user's netid."""
    # Ensure the profile netid matches the authenticated user
    if profile.netid != current_user.netid:
        raise HTTPException(status_code=403, detail="Cannot create profile for different user")
    return {"message": "Profile successfully created.", "profile": create_user_profile(profile)}

@router.get("/profile/me")
def read_profile(current_user: UserProfileDB = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    return current_user

@router.put("/profile/me")
def update_profile(
    profile: UserProfile,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Update current authenticated user's profile."""
    # Ensure the profile netid matches the authenticated user
    if profile.netid != current_user.netid:
        raise HTTPException(status_code=403, detail="Cannot update profile for different user")
    updated_profile = update_user_profile(current_user.netid, profile)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Profile updated", "profile": updated_profile}
