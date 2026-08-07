"""
AGENT TOOLS LAYER
Gives all agents tool access to:
- Gmail (send real emails)
- Google Calendar (create real events)
- Database (read + write everything)

Every WRITE tool automatically saves to the database.
"""

# =============================================
# EMAIL TOOLS
# =============================================
def tool_send_email(to, subject, body, cc=None):
    """Send a real email via Gmail AND save to database"""
    from Backend.services.gmail_service import send_draft_email
    from Backend.database.crud import log_email

    result = send_draft_email(to=to, subject=subject, body=body, cc=cc)

    # Auto-log to database
    try:
        log_email(
            to_emails=", ".join(to) if isinstance(to, list) else str(to),
            subject=subject,
            body=body,
            status="sent",
            message_id=result.get("message_id", ""),
        )
    except Exception:
        pass

    return result


def tool_log_email(to_emails, subject, body, status="draft", message_id=""):
    """Save email record to database WITHOUT sending"""
    from Backend.database.crud import log_email
    log_email(to_emails=to_emails, subject=subject, body=body,
              status=status, message_id=message_id)


# =============================================
# CALENDAR TOOLS
# =============================================
def tool_create_event(title, date, time, duration_minutes=30,
                      attendees=None, location="", description="",
                      timezone="UTC"):
    """Create a real Google Calendar event AND save to database"""
    from Backend.services.calendar_service import create_calendar_event
    from Backend.database.crud import log_event

    result = create_calendar_event(
        title=title, date=date, time=time,
        duration_minutes=duration_minutes,
        attendees=attendees or [],
        location=location, description=description, timezone=timezone,
    )

    # Auto-log to database
    try:
        log_event(
            title=title, date=date, time=time,
            duration_minutes=duration_minutes,
            attendees=", ".join(attendees) if attendees else "",
            location=location, description=description,
            calendar_link=result.get("link", ""),
            status="created",
        )
    except Exception:
        pass

    return result


# =============================================
# DATABASE WRITE TOOLS
# =============================================
def tool_log_chat(role, content, intent=None):
    from Backend.database.crud import log_chat
    log_chat(role, content, intent)

def tool_log_research(query, result):
    from Backend.database.crud import log_research
    log_research(query, result)

def tool_log_meeting(query, result, task="auto"):
    from Backend.database.crud import log_meeting
    log_meeting(query, result, task)

def tool_log_upload(filename, file_path, query, result):
    from Backend.database.crud import log_upload
    log_upload(filename, file_path, query, result)


# =============================================
# DATABASE