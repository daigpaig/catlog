from fastapi import APIRouter, Depends
from ..schemas.chat import ChatRequest
from ..services.openai_service import get_chat_response
from ..services.llm.tools_impl import recommend_courses
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
    
    # Try to use recommend_courses for course-related queries
    # This will return structured data if it's a course recommendation
    message_lower = request.message.lower()
    course_keywords = ["course", "class", "recommend", "find", "take", "enroll", "schedule", "elective", "requirement"]
    
    if any(keyword in message_lower for keyword in course_keywords):
        try:
            result = recommend_courses(request.message)
            if isinstance(result, dict) and "structured_data" in result:
                return {
                    "response": result.get("content", ""),
                    "structuredData": result.get("structured_data")
                }
            # Fallback to string response
            return {"response": result if isinstance(result, str) else result.get("content", "")}
        except Exception as e:
            print(f"Error in recommend_courses: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to regular chat
            pass
    
    # Default to regular chat response
    try:
        response = get_chat_response(chat_request)
        return {"response": response}
    except Exception as e:
        print(f"Error in get_chat_response: {e}")
        import traceback
        traceback.print_exc()
        return {"response": "Sorry, something went wrong. Please try again."}