from pydantic import BaseModel
from typing import Optional, List

class ScheduleCreate(BaseModel):
    name: str
    term: str
    # netid, created, updated will be auto-set by the backend

class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    term: Optional[str] = None

class ScheduleCourseCreate(BaseModel):
    section_id: str
    course_subject: Optional[str] = None
    course_number: Optional[str] = None
    course_title: Optional[str] = None
    section_number: Optional[str] = None
    meeting_days: Optional[List[str]] = None
    start_end: Optional[List[List[str]]] = None  # [[start, end], ...]
    instructors: Optional[List[str]] = None
    color: Optional[str] = None  # Hex color code (e.g., "#3b82f6")