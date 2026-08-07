from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from Backend.agents.router import route_to_agent

router = APIRouter(prefix="/router", tags=["router"])


# === JSON Request (for regular chat) ===
class RouterRequest(BaseModel):
    query: str

class RouterResponse(BaseModel):
    response: str
    intent: str

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
async def router_chat(request: RouterRequest):
    """Main endpoint — routes ALL messages to correct agent"""
    result = route_to_agent(request.query)
    return RouterResponse(response=result["response"], intent=result["intent"])


# === FormData Request (for file uploads) ===
@router.post("/chat-with-file")
async def router_chat_with_file(
    file: UploadFile = File(...),
    query: str = Form(default=""),
):
    """Endpoint for messages with file attachments"""
    allowed_types = ["application/pdf", "text/plain", "text/csv"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    content = await file.read()

    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 20MB.")

    result = route_to_agent(
        user_input=query or f"Analyze this file: {file.filename}",
        file_content=content,
        filename=file.filename,
    )

    return RouterResponse(response=result["response"], intent=result["intent"])