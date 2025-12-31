from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import engine
from ..models.db_models import ScheduleDB, UserProfileDB
from ..auth.dependencies import get_current_user

router = APIRouter()

@router.post("/schedule")
def create_new_schedule(
    schedule: ScheduleDB,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Create or update a schedule for the authenticated user."""
    # Ensure the schedule belongs to the authenticated user
    if schedule.netid != current_user.netid:
        raise HTTPException(status_code=403, detail="Cannot create schedule for different user")
    
    with Session(engine) as session:
        existing = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule.id)).first()
        if existing:
            # Ensure existing schedule belongs to user
            if existing.netid != current_user.netid:
                raise HTTPException(status_code=403, detail="Cannot modify schedule for different user")
            for field, value in schedule.dict().items():
                setattr(existing, field, value)
        else:
            session.add(schedule)
        session.commit()
        return {"message": "Schedule saved."}
    
@router.get("/schedule")
def retrieve_schedules(current_user: UserProfileDB = Depends(get_current_user)):
    """Get all schedules for the authenticated user."""
    with Session(engine) as session:
        schedules = session.exec(select(ScheduleDB).where(ScheduleDB.netid == current_user.netid)).all()
        return [s.dict() for s in schedules]
    

@router.get("/schedule/{schedule_id}")
def get_schedule(
    schedule_id: int,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Get a specific schedule - ensures it belongs to the authenticated user."""
    with Session(engine) as session:
        schedule = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule_id)).first()
        if schedule:
            if schedule.netid != current_user.netid:
                raise HTTPException(status_code=403, detail="Cannot access schedule for different user")
            return schedule.dict()
        raise HTTPException(status_code=404, detail="Schedule not found.")
    
@router.delete("/schedule/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Delete a schedule - ensures it belongs to the authenticated user."""
    with Session(engine) as session:
        schedule = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule_id)).first()
        if schedule:
            if schedule.netid != current_user.netid:
                raise HTTPException(status_code=403, detail="Cannot delete schedule for different user")
            session.delete(schedule)
            session.commit()
            return {"message": "Schedule deleted."}
        raise HTTPException(status_code=404, detail="Schedule not found.")