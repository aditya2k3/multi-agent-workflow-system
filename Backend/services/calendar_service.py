from googleapiclient.discovery import build
from datetime import datetime, timedelta
from Backend.services.google_auth_service import get_authenticated_credentials


def create_calendar_event(
    title: str,
    date: str,
    time: str,
    duration_minutes: int = 30,
    attendees: list = None,
    location: str = "",
    description: str = "",
    timezone: str = "UTC",
) -> dict:
    """
    Creates a real Google Calendar event.
    
    Args:
        title: Event title
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (24-hour)
        duration_minutes: How long the event lasts
        attendees: List of email addresses to invite
        location: Physical location or video link
        description: Event description
        timezone: IANA timezone string
    
    Returns:
        Dict with event details including HTML link
    """
    creds = get_authenticated_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Build start/end times
    start_datetime = f"{date}T{time}:00"
    end_dt = datetime.strptime(f"{date}T{time}", "%Y-%m-%dT%H:%M") + timedelta(minutes=duration_minutes)
    end_datetime = end_dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Build event body
    event_body = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_datetime,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": timezone,
        },
    }

    # Add location if provided
    if location:
        event_body["location"] = location

    # Add attendees if provided
    if attendees:
        event_body["attendees"] = [{"email": email} for email in attendees]
        # Send email invitations to attendees
        event_body["sendUpdates"] = "all"

    # Create the event
    event = service.events().insert(
        calendarId="primary",
        body=event_body,
        sendUpdates="all" if attendees else "none",
    ).execute()

    return {
        "event_id": event["id"],
        "title": event["summary"],
        "link": event.get("htmlLink", ""),
        "start": event["start"].get("dateTime", ""),
        "end": event["end"].get("dateTime", ""),
        "attendees": [a["email"] for a in event.get("attendees", [])],
        "status": "created",
    }