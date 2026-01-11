from pydantic import BaseModel
from typing import List, Optional

class UserProfile(BaseModel):
    netid: str
    majors: List[str]
    minors: Optional[List[str]] = []
    classes_already_taken: Optional[List[str]] = []
    vocational_interests: Optional[List[str]] = []
    favorite_profs: Optional[List[str]] = []
    disliked_profs: Optional[List[str]] = []
    earliest_class_time: Optional[str] = None  # e.g., "10:00"
    locked_classes: Optional[List[str]] = []
    self_description: Optional[str] = None
    unavailable_times: Optional[List[str]] = []  # e.g., ["Mon-8", "Tue-9"] - format: "Day-Hour"
    prefer_avoid_times: Optional[List[str]] = []  # e.g., ["Wed-14", "Thu-15"] - format: "Day-Hour"