from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from Backend.agents.research_agent import run_research_agent

router = APIRouter(prefix="/analysis", tags=["analysis"])


class ResearchRequest(BaseModel):
    query: str
    task: str = "auto"


class ResearchResponse(BaseModel):
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


@router.post("/research")
async def research_endpoint(request: ResearchRequest):
    result = run_research_agent(request.query, request.task)
    return ResearchResponse(response=result)