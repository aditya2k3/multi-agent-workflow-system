from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from Backend.agents.scheduler_agent import run_scheduler_agent

router = APIRouter(prefix="/schedule", tags=["schedule"])


class ScheduleRequest(BaseModel):
    query: str
    task: str = "auto"


class ScheduleResponse(BaseModel):
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


@router.post("/create")
async def schedule_event(request: ScheduleRequest):
    result = run_scheduler_agent(request.query, request.task)
    return ScheduleResponse(response=result)