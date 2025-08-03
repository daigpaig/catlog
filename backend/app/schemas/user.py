from pydantic import BaseModel
from typing import List, Optional

class UserProfile(BaseModel):
    netid: str
    majors: List[str]
    minors: Optional[List[str]] = []
    classes_already_taken: Optional[List[str]] = "No info on already taken classes"
    vocational_interests: Optional[List[str]] = "No info on vocational interests"
    favorite_profs: Optional[List[str]] = []
    disliked_profs: Optional[List[str]] = []
    earliest_class_time: Optional[str] = None  # e.g., "10:00"
    locked_classes: Optional[List[str]] = []