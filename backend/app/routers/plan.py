from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..services.llm.tool_runner import run_pipeline_with_tools

router = APIRouter()

@router.post("/plan/shortlist")
def plan_shortlist(payload: dict):
    message = payload.get("message","")
    profile = payload.get("profile",{})
    term_hint = payload.get("term_hint")
    return JSONResponse(run_pipeline_with_tools(message, profile, term_hint))


