from fastapi import APIRouter
from services.db_service import get_user_by_netid

router = APIRouter()

@router.get("/test_user/{netid}")
def test_get_user(netid: str):
    user = get_user_by_netid(netid)
    if user:
        return user
    else:
        return {"error": "User not found"}