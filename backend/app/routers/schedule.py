from fastapi import APIRouter
from sqlmodel import Session, select
from database import engine
from models.db_models import ScheduleDB

router = APIRouter()

@router.post("/schedule")
def create_new_schedule(schedule: ScheduleDB):
    with Session(engine) as session:
        existing = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule.id)).first()
        if existing:
            for field, value in schedule.dict().items():
                setattr(existing, field, value)
        else:
            session.add(schedule)
        session.commit()
        return {"message": "Schedule saved."}
    
@router.get("/schedule")
def retrieve_schedules(netid: str):
    with Session(engine) as session:
        schedules = session.exec(select(ScheduleDB).where(ScheduleDB.netid == netid)).all()
        return [s.dict() for s in schedules]
    

@router.get("/schedule/{schedule_id}")
def get_schedule(schedule_id: int):
    with Session(engine) as session:
        schedule = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule_id)).first()
        if schedule:
            return schedule.dict()
        return {"error": "Schedule not found."}
    
@router.delete("/schedule/{schedule_id}")
def delete_schedule(schedule_id: int):
    with Session(engine) as session:
        schedule = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule_id)).first()
        if schedule:
            session.delete(schedule)
            session.commit()
            return {"message": "Schedule deleted."}
        return {"error": "Schedule not found."}