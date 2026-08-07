import json
from datetime import datetime
from Backend.services.gemini_service import call_gemini
from Backend.services.calendar_service import create_calendar_event
from Backend.services.gmail_service import send_event_invitation_email
from Backend.prompts.schedule_prompt import (
    SCHEDULE_SYSTEM_PROMPT,
    PARSE_EVENT_PROMPT,
)


def parse_event(user_input: str) -> dict:
    """Parse natural language into structured event data using DeepSeek"""
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = PARSE_EVENT_PROMPT.format(
        system_prompt=SCHEDULE_SYSTEM_PROMPT,
        user_input=user_input,
        today=today,
    )

    response = call_gemini(prompt)

    try:
        # Extract JSON from response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        elif "{" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
        else:
            json_str = response.strip()

        return json.loads(json_str)

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        return {"error": f"Could not parse: {str(e)}", "raw_response": response}


def schedule_and_notify(user_input: str) -> str:
    """
    Full flow:
    1. Parse natural language → structured event (DeepSeek)
    2. Create Google Calendar event (Calendar API)
    3. Send invitation email to attendees (Gmail API)
    4. Save to database (tool access)
    5. Return confirmation
    """

    # Step 1: Parse with DeepSeek
    event_data = parse_event(user_input)

    if "error" in event_data:
        return f"⚠️ Parsing failed: {event_data['error']}\n\nRaw: {event_data.get('raw_response', '')}"

    # Check for missing critical fields
    missing = event_data.get("missing_fields", [])
    if "date" in str(missing).lower() or "time" in str(missing).lower():
        return (
            f"⚠️ I couldn't determine all event details.\n\n"
            f"Parsed so far:\n"
            f"• Title: {event_data.get('title', 'N/A')}\n"
            f"• Date: {event_data.get('date', 'MISSING')}\n"
            f"• Time: {event_data.get('time', 'MISSING')}\n"
            f"• Attendees: {', '.join(event_data.get('attendees', [])) or 'None'}\n\n"
            f"Missing: {', '.join(missing)}\n"
            f"Please provide the missing details."
        )

    # Step 2: Create Google Calendar Event
    try:
        calendar_result = create_calendar_event(
            title=event_data.get("title", "Untitled Meeting"),
            date=event_data["date"],
            time=event_data["time"],
            duration_minutes=event_data.get("duration_minutes", 30),
            attendees=event_data.get("attendees", []),
            location=event_data.get("location", ""),
            description=event_data.get("description", ""),
            timezone=event_data.get("timezone", "UTC"),
        )
    except Exception as e:
        return f"⚠️ Calendar creation failed: {str(e)}"

    # Step 3: Send invitation email
    attendees = event_data.get("attendees", [])
    email_result = None

    if attendees:
        try:
            email_result = send_event_invitation_email(
                to=attendees,
                title=event_data.get("title", "Untitled Meeting"),
                date=event_data["date"],
                time=event_data["time"],
                duration_minutes=event_data.get("duration_minutes", 30),
                location=event_data.get("location", ""),
                description=event_data.get("description", ""),
                calendar_link=calendar_result.get("link", ""),
            )
        except Exception as e:
            email_result = {"error": str(e)}

    # Step 4: Save to database (tool access) ← INSIDE the function, BEFORE return
    try:
        from Backend.database.crud import log_event
        log_event(
            title=event_data.get("title", "Untitled"),
            date=event_data.get("date", ""),
            time=event_data.get("time", ""),
            duration_minutes=event_data.get("duration_minutes", 30),
            attendees=", ".join(event_data.get("attendees", [])),
            location=event_data.get("location", ""),
            description=event_data.get("description", ""),
            calendar_link=calendar_result.get("link", ""),
            status="created",
        )
    except Exception:
        pass

    # Step 5: Build confirmation message
    confirmation = f"""✅ EVENT CREATED SUCCESSFULLY

📅 Title: {calendar_result['title']}
📆 Date: {calendar_result['start']}
🔗 Calendar Link: {calendar_result['link']}
👥 Attendees: {', '.join(calendar_result['attendees']) or 'None'}

📧 EMAIL NOTIFICATION:"""

    if email_result and email_result.get("status") == "sent":
        confirmation += f"\n   ✅ Invitation sent to: {', '.join(email_result['to'])}"
    elif email_result and "error" in email_result:
        confirmation += f"\n   ⚠️ Email failed: {email_result['error']}"
    else:
        confirmation += "\n   ℹ️ No attendees to notify"

    return confirmation


def run_scheduler_agent(query: str, task: str = "auto") -> str:
    """Main entry point called by API layer"""
    task = task.lower().strip()

    if task == "parse":
        event_data = parse_event(query)
        return json.dumps(event_data, indent=2)
    else:
        return schedule_and_notify(query)