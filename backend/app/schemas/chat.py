from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    user_id: str
    timestamp: str
    majors: Optional[list[str]] = None
    minors: Optional[list[str]] = None
    schedule_preferences: Optional[str] = None
    self_description: Optional[str] = None
    locked_classes: Optional[list[str]] = None