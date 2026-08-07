from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from Backend.database.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)              # "user" or "ai"
    content = Column(Text)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ScheduledEvent(Base):
    __tablename__ = "scheduled_events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    date = Column(String)
    time = Column(String)
    duration_minutes = Column(Integer, default=30)
    attendees = Column(Text, default="")
    location = Column(String, default="")
    description = Column(Text, default="")
    calendar_link = Column(String, default="")
    status = Column(String, default="created")
    created_at = Column(DateTime, server_default=func.now())


class SentEmail(Base):
    __tablename__ = "sent_emails"
    id = Column(Integer, primary_key=True, index=True)
    to_emails = Column(Text)
    subject = Column(String)
    body = Column(Text)
    status = Column(String, default="sent")
    message_id = Column(String, default="")
    created_at = Column(DateTime, server_default=func.now())


class ResearchHistory(Base):
    __tablename__ = "research_history"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class MeetingHistory(Base):
    __tablename__ = "meeting_history"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text)
    result = Column(Text)
    task = Column(String, default="auto")
    created_at = Column(DateTime, server_default=func.now())


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    query = Column(Text, default="")
    result = Column(Text)
    created_at = Column(DateTime, server_default=func.now())