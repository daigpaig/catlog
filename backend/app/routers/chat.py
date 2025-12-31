from fastapi import APIRouter, Depends
from ..schemas.chat import ChatRequest
from ..services.openai_service import get_chat_response
from ..auth.dependencies import get_current_user
from ..models.db_models import UserProfileDB
from datetime import datetime

router = APIRouter()

@router.post("/chat")
def chat(
    request: ChatRequest,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Chat endpoint that uses authenticated user's profile data."""
    # Populate chat request with user data from authenticated user
    chat_request = ChatRequest(
        message=request.message,
        user_id=current_user.netid,
        timestamp=request.timestamp or datetime.utcnow().isoformat(),
        majors=request.majors or current_user.majors,
        minors=request.minors or current_user.minors,
        schedule_preferences=request.schedule_preferences or (
            f"Earliest class time: {current_user.earliest_class_time}" 
            if current_user.earliest_class_time else None
        ),
        self_description=request.self_description or current_user.self_description,
        locked_classes=request.locked_classes or current_user.locked_classes,
    )
    print("Received request:", chat_request)
    response = get_chat_response(chat_request)
    return {"response": response}