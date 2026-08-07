import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from Backend.services.google_auth_service import get_authenticated_credentials


# =============================================
# EXISTING FUNCTIONS (from Schedule Agent)
# =============================================

def send_email(to: list, subject: str, body: str, cc: list = None) -> dict:
    """Sends a real email from the authenticated Gmail account"""
    creds = get_authenticated_credentials()
    service = build("gmail", "v1", credentials=creds)

    message = MIMEMultipart("alternative")
    message["to"] = ", ".join(to)
    message["subject"] = subject
    if cc:
        message["cc"] = ", ".join(cc)

    html_part = MIMEText(body, "html")
    message.attach(html_part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent_message = (
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
    )

    return {
        "message_id": sent_message["id"],
        "to": to,
        "subject": subject,
        "status": "sent",
    }


def send_event_invitation_email(
    to: list, title: str, date: str, time: str,
    duration_minutes: int, location: str, description: str, calendar_link: str,
) -> dict:
    """Sends a formatted event invitation email"""
    attendees_html = "".join(f"<li>{email}</li>" for email in to)

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4f7df9;">📅 Meeting Invitation</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr><td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Event</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{title}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Date</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{date} at {time}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Duration</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{duration_minutes} minutes</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Location</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{location or 'Not specified'}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Attendees</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;"><ul>{attendees_html}</ul></td></tr>
        </table>
        <p style="color: #555;">{description}</p>
        <a href="{calendar_link}" style="display: inline-block; padding: 12px 24px; background: #4f7df9; 
           color: white; text-decoration: none; border-radius: 8px; margin-top: 10px;">
            📅 View in Google Calendar</a>
        <p style="color: #999; font-size: 12px; margin-top: 20px;">Sent via Enterprise AI Assistant</p>
    </div>"""

    return send_email(to=to, subject=f"📅 Meeting Invitation: {title} — {date} at {time}", body=html_body)


# =============================================
# NEW FUNCTIONS (for Email Agent)
# =============================================

def send_draft_email(to: list, subject: str, body: str, cc: list = None) -> dict:
    """
    Sends an AI-drafted email.
    Wraps send_email with HTML formatting for professional look.
    """
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.6;">
        {body}
        <br><br>
        <p style="color: #999; font-size: 11px; border-top: 1px solid #eee; padding-top: 10px;">
            ✉️ Sent via Enterprise AI Assistant
        </p>
    </div>"""

    return send_email(to=to, subject=subject, body=html_body, cc=cc)


def get_recent_emails(max_results: int = 5, query: str = "") -> list:
    """
    Fetches recent emails from Gmail for context-aware replies.
    
    Args:
        max_results: Number of emails to fetch
        query: Gmail search query (e.g., "from:john@company.com")
    
    Returns:
        List of email summaries
    """
    creds = get_authenticated_credentials()
    service = build("gmail", "v1", credentials=creds)

    # Search messages
    search_query = query if query else "in:inbox"
    results = (
        service.users()
        .messages()
        .list(userId="me", q=search_query, maxResults=max_results)
        .execute()
    )

    emails = []
    for msg_info in results.get("messages", []):
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_info["id"], format="metadata", metadataHeaders=["From", "Subject", "Date"])
            .execute()
        )

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

        # Get snippet (preview text)
        emails.append({
            "id": msg["id"],
            "from": headers.get("From", "Unknown"),
            "subject": headers.get("Subject", "No Subject"),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })

    return emails