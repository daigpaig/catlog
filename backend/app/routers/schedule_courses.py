from fastapi import APIRouter
from sqlmodel import Session, select
from database import engine
from models.db_models import ScheduleCourseDB

router = APIRouter()

@router.post("/schedule/{schedule_id}/courses")
def add_course(schedule_id: int, schedule_course: ScheduleCourseDB):
    with Session(engine) as session:
        existing = session.exec(
            select(ScheduleCourseDB).where(
                ScheduleCourseDB.id == schedule_course.id,
                ScheduleCourseDB.schedule_id == schedule_id
            )
        ).first()
        if existing:
            for field, value in schedule_course.dict().items():
                setattr(existing, field, value)
        else:
            session.add(schedule_course)
        session.commit()
        return {"message": "Course added."}


@router.delete("/schedule/{schedule_id}/courses/{schedule_course_id}")
def remove_course(schedule_id: int, schedule_course_id: int):
    with Session(engine) as session:
        sched_course = session.exec(
            select(ScheduleCourseDB).where(
                ScheduleCourseDB.id == schedule_course_id,
                ScheduleCourseDB.schedule_id == schedule_id
            )
        ).first()
        if sched_course:
            session.delete(sched_course)
            session.commit()
            return {"message": "Course deleted."}
        return {"error": "Course not found."}