from Backend.database.database import SessionLocal
from Backend.database.models import (
    ChatMessage, ScheduledEvent, SentEmail,
    ResearchHistory, MeetingHistory, UploadedFile,
)

# =============================================
# CHAT (used by API with Depends(get_db))
# =============================================
def save_chat_message(db, role, content, intent=None):
    msg = ChatMessage(role=role, content=content, intent=intent)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_chat_history(db, limit=50):
    return db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(limit).all()


# =============================================
# EVENTS
# =============================================
def save_scheduled_event(db, title, date, time, duration_minutes=30,
                         attendees="", location="", description="",
                         calendar_link="", status="created"):
    event = ScheduledEvent(
        title=title, date=date, time=time,
        duration_minutes=duration_minutes, attendees=attendees,
        location=location, description=description,
        calendar_link=calendar_link, status=status,
    )
    db.add(event)
    db.commit()
    return event


def get_scheduled_events(db, limit=50):
    return db.query(ScheduledEvent).order_by(ScheduledEvent.created_at.desc()).limit(limit).all()


# =============================================
# EMAILS
# =============================================
def save_sent_email(db, to_emails, subject, body, status="sent", message_id=""):
    email = SentEmail(to_emails=to_emails, subject=subject, body=body,
                      status=status, message_id=message_id)
    db.add(email)
    db.commit()
    return email


def get_sent_emails(db, limit=50):
    return db.query(SentEmail).order_by(SentEmail.created_at.desc()).limit(limit).all()


# =============================================
# RESEARCH
# =============================================
def save_research(db, query, result):
    r = ResearchHistory(query=query, result=result)
    db.add(r)
    db.commit()
    return r


def get_research_history(db, limit=50):
    return db.query(ResearchHistory).order_by(ResearchHistory.created_at.desc()).limit(limit).all()


# =============================================
# MEETINGS
# =============================================
def save_meeting(db, query, result, task="auto"):
    m = MeetingHistory(query=query, result=result, task=task)
    db.add(m)
    db.commit()
    return m


def get_meeting_history(db, limit=50):
    return db.query(MeetingHistory).order_by(MeetingHistory.created_at.desc()).limit(limit).all()


# =============================================
# FILES
# =============================================
def save_uploaded_file(db, filename, file_path, query="", result=""):
    f = UploadedFile(filename=filename, file_path=file_path, query=query, result=result)
    db.add(f)
    db.commit()
    return f


def get_uploaded_files(db, limit=50):
    return db.query(UploadedFile).order_by(UploadedFile.created_at.desc()).limit(limit).all()


# =============================================
# AGENT LOGGERS — agents call these directly (tool access)
# They open their own session, so agents need 1 line only
# =============================================
def log_chat(role, content, intent=None):
    with SessionLocal() as db:
        save_chat_message(db, role, content, intent)

def log_event(**kwargs):
    with SessionLocal() as db:
        save_scheduled_event(db, **kwargs)

def log_email(**kwargs):
    with SessionLocal() as db:
        save_sent_email(db, **kwargs)

def log_research(query, result):
    with SessionLocal() as db:
        save_research(db, query, result)

def log_meeting(query, result, task="auto"):
    with SessionLocal() as db:
        save_meeting(db, query, result, task)

def log_upload(filename, file_path, query="", result=""):
    with SessionLocal() as db:
        save_uploaded_file(db, filename, file_path, query, result)