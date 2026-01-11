from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import engine
from ..models.db_models import ScheduleDB, UserProfileDB
from ..schemas.schedule import ScheduleCreate, ScheduleUpdate
from ..auth.dependencies import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/schedule")
def create_new_schedule(
    schedule_data: ScheduleCreate,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Create a new schedule for the authenticated user."""
    now = datetime.utcnow().isoformat()
    
    schedule = ScheduleDB(
        netid=current_user.netid,
        name=schedule_data.name,
        term=schedule_data.term,
        created=now,
        updated=now
    )
    
    with Session(engine) as session:
        session.add(schedule)
        session.commit()
        session.refresh(schedule)
        return schedule.dict()

@router.put("/schedule/{schedule_id}")
def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Update an existing schedule for the authenticated user."""
    with Session(engine) as session:
        schedule = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule_id)).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found.")
        if schedule.netid != current_user.netid:
            raise HTTPException(status_code=403, detail="Cannot modify schedule for different user")
        
        if schedule_data.name is not None:
            schedule.name = schedule_data.name
        if schedule_data.term is not None:
            schedule.term = schedule_data.term
        schedule.updated = datetime.utcnow().isoformat()
        
        session.commit()
        session.refresh(schedule)
        return schedule.dict()
    
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