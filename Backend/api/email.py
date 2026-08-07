from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from Backend.agents.email_agent import run_email_agent

router = APIRouter(prefix="/email", tags=["email"])


class EmailRequest(BaseModel):
    query: str
    task: str = "auto"


class EmailResponse(BaseModel):
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


@router.post("/send")
async def email_endpoint(request: EmailRequest):
    result = run_email_agent(request.query, request.task)
    return EmailResponse(response=result)