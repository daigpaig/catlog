from fastapi import APIRouter
from schemas.chat import ChatRequest
from services.openai_service import get_chat_response
from services.db_service import get_user_by_netid

router = APIRouter()

@router.post("/chat")
def chat(request: ChatRequest):
    print("Received request:", request)
    response = get_chat_response(request)
    return {"response": response}