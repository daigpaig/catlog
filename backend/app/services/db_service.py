from sqlmodel import Session, select
from ..database import engine
from ..models.db_models import UserProfileDB
from ..schemas.user import UserProfile
from typing import Optional

def get_user_by_netid(netid: str) -> Optional[UserProfileDB]:
    with Session(engine) as session:
        statement = select(UserProfileDB).where(UserProfileDB.netid == netid)
        result = session.exec(statement).first()
        return result
    
def create_user_profile(profile: UserProfile) -> Optional[UserProfileDB]:
    with Session(engine) as session:
        profile_db = UserProfileDB.from_orm(profile)
        session.add(profile_db)
        session.commit()
        session.refresh(profile_db)
        return profile_db

def update_user_profile(netid: str, profile: UserProfile) -> Optional[UserProfileDB]:
    with Session(engine) as session:
        profile_db = session.get(UserProfileDB, netid)
        if not profile_db:
            return None
        for field, value in profile.dict().items():
            setattr(profile_db, field, value)
        session.commit()
        session.refresh(profile_db)
        return profile_db