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

class ScheduleDB(SQLModel, table = True):
    id: int = Field(default = None, primary_key = True)
    netid: str
    name: Optional[str] = "Schedule"
    term: str
    created: str
    updated: str

class ScheduleCoursesDB(SQLModel, table = True):
    id: int = Field(default = None, primary_key = True)
    schedule_id: str
    section_id: str
    
