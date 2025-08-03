from fastapi import APIRouter, HTTPException
from schemas.user import UserProfile
from services.db_service import create_user_profile, get_user_by_netid, update_user_profile

router = APIRouter()

@router.post("/profile")
def create_profile(profile: UserProfile):
    return {"message": "Profile successfully created.", "profile": create_user_profile(profile)}

@router.get("/profile/{netid}")
def read_profile(netid: str):
    user = get_user_by_netid(netid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/profile/{netid}")
def update_profile(netid: str, profile: UserProfile):
    updated_profile = update_user_profile(netid, profile)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Profile updated", "profile": updated_profile}
