from fastapi import APIRouter
from sqlmodel import Session
from database import engine
from models.db_models import UserProfileDB

router = APIRouter()

@router.post("/profile")
def create_or_update_profile(profile: UserProfileDB):
    with Session(engine) as session:
        existing = session.query(UserProfileDB).filter(UserProfileDB.netid == profile.netid).first()
        if existing:
            for field, value in profile.dict().items():
                setattr(existing, field, value)
        else:
            session.add(profile)
        session.commit()
        return {"message": "Profile saved."}

@router.get("/profile/{netid}")
def get_profile(netid: str):
    with Session(engine) as session:
        profile = session.query(UserProfileDB).filter(UserProfileDB.netid == netid).first()
        return profile