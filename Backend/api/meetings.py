from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from Backend.agents.meeting_agent import run_meeting_agent

router = APIRouter(prefix="/meeting", tags=["meeting"])


class MeetingRequest(BaseModel):
    query: str
    task: str = "auto"


class MeetingResponse(BaseModel):
    response: str

    @field_validator("response", mode="before")
    @classmethod
    def extract_text(cls, v):
        if isinstance(v, list):
            return " ".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in v
            )
        if isinstance(v, str):
            return v
        return str(v)


@router.post("/chat")
async def meeting_chat(request: MeetingRequest):
    result = run_meeting_agent(request.query, request.task)
    return MeetingResponse(response=result)