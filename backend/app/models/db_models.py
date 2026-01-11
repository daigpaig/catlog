from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List

class UserProfileDB(SQLModel, table=True):
    netid: str = Field(primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    majors: List[str] = Field(sa_column=Column(JSON))
    minors: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    
    classes_already_taken: Optional[List[str]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    vocational_interests: Optional[List[str]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    
    favorite_profs: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    disliked_profs: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    
    earliest_class_time: Optional[str] = None
    locked_classes: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    self_description: Optional[str] = None
    unavailable_times: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))  # e.g., ["Mon-8", "Tue-9"]
    prefer_avoid_times: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))  # e.g., ["Wed-14", "Thu-15"]

class ScheduleDB(SQLModel, table = True):
    id: int = Field(default = None, primary_key = True)
    netid: str
    name: Optional[str] = "Schedule"
    term: str
    created: str
    updated: str

class ScheduleCoursesDB(SQLModel, table = True):
    id: int = Field(default = None, primary_key = True)
    schedule_id: int
    section_id: str
    # Store section metadata for calendar display
    course_subject: Optional[str] = None
    course_number: Optional[str] = None
    course_title: Optional[str] = None
    section_number: Optional[str] = None
    meeting_days: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    start_end: Optional[List[List[str]]] = Field(default_factory=list, sa_column=Column(JSON))  # [[start, end], ...]
    instructors: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    color: Optional[str] = None  # Hex color code for calendar display (paper.nu style)
    
