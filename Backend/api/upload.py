from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, field_validator
from Backend.agents.upload_agent import run_upload_agent

router = APIRouter(prefix="/upload", tags=["upload"])


class UploadResponse(BaseModel):
    response: str
    filename: str

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


@router.post("/analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    query: str = Form(default=""),
    task: str = Form(default="auto"),
):
    # Validate file type
    allowed_types = ["application/pdf", "text/plain", "text/csv"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Use PDF, TXT, or CSV."
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size (max 20MB)
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 20MB.")
    
    # Process through agent
    result = run_upload_agent(
        file_content=content,
        filename=file.filename,
        query=query,
        task=task,
    )
    
    return UploadResponse(response=result, filename=file.filename)