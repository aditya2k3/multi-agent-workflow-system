from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Backend.database.database import get_db
from Backend.database.crud import (
    get_chat_history, get_scheduled_events,
    get_sent_emails, get_research_history,
    get_meeting_history, get_uploaded_files,
    save_chat_message,
)

router = APIRouter(prefix="/history", tags=["history"])


def to_list(rows):
    """Convert ORM objects to plain dicts for JSON response"""
    return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]


@router.get("/chat")
def chat_history(limit: int = 50, db: Session = Depends(get_db)):
    return to_list(get_chat_history(db, limit))

@router.get("/events")
def event_history(limit: int = 50, db: Session = Depends(get_db)):
    return to_list(get_scheduled_events(db, limit))

@router.get("/emails")
def email_history(limit: int = 50, db: Session = Depends(get_db)):
    return to_list(get_sent_emails(db, limit))

@router.get("/research")
def research_history(limit: int = 50, db: Session = Depends(get_db)):
    return to_list(get_research_history(db, limit))

@router.get("/meetings")
def meeting_history(limit: int = 50, db: Session = Depends(get_db)):
    return to_list(get_meeting_history(db, limit))

@router.get("/files")
def file_history(limit: int = 50, db: Session = Depends(get_db)):
    return to_list(get_uploaded_files(db, limit))