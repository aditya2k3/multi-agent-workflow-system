from Backend.services.gemini_service import call_gemini
from Backend.prompts.router_prompt import ROUTER_SYSTEM_PROMPT, ROUTER_CLASSIFY_PROMPT

# Import all agents
from Backend.agents.meeting_agent import run_meeting_agent
from Backend.agents.upload_agent import run_upload_agent
from Backend.agents.research_agent import run_research_agent
from Backend.agents.scheduler_agent import run_scheduler_agent
from Backend.agents.email_agent import run_email_agent


def classify_intent(user_input: str) -> str:
    """Use DeepSeek to classify user intent into one category"""
    prompt = ROUTER_CLASSIFY_PROMPT.format(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        user_input=user_input,
    )

    response = call_gemini(prompt).strip().lower()

    # Validate response — only accept known categories
    valid_categories = ["meeting", "upload", "research", "schedule", "email", "history", "chat"]

    for category in valid_categories:
        if category in response:
            return category

    return "chat"


def route_to_agent(user_input: str, file_content: bytes = None, filename: str = None) -> dict:
    """
    Main router:
    1. Classify intent
    2. Route to correct agent
    3. Log conversation to database
    4. Return response + metadata
    """

    # Step 1: Classify
    intent = classify_intent(user_input)

    # Step 2: Route to correct agent
    try:
        if intent == "meeting":
            response = run_meeting_agent(user_input)
        elif intent == "upload":
            if file_content and filename:
                response = run_upload_agent(file_content, filename, user_input)
            else:
                response = "📎 Please attach a file first by clicking the paperclip icon, then describe what you need."
        elif intent == "research":
            response = run_research_agent(user_input)
        elif intent == "schedule":
            response = run_scheduler_agent(user_input)
        elif intent == "email":
            response = run_email_agent(user_input)
        elif intent == "history":
            response = handle_history(user_input)
        else:
            response = general_chat(user_input)

    except Exception as e:
        response = f"⚠️ Error in {intent} agent: {str(e)}"

    # Step 3: Save conversation to database
    try:
        from Backend.database.crud import log_chat
        log_chat("user", user_input, intent)
        log_chat("ai", response, intent)
    except Exception:
        pass

    # Step 4: Return
    return {"response": response, "intent": intent}


def handle_history(query: str) -> str:
    """Tool access: read from database based on user query"""
    from Backend.database.database import SessionLocal
    from Backend.database.crud import (
        get_scheduled_events, get_sent_emails, get_research_history,
        get_chat_history, get_meeting_history, get_uploaded_files,
    )

    q = query.lower()

    with SessionLocal() as db:
        if any(w in q for w in ["event", "schedule", "calendar", "meeting booked"]):
            rows = get_scheduled_events(db, 10)
            if not rows:
                return "📭 No scheduled events found in your database."
            out = "📅 YOUR SCHEDULED EVENTS:\n\n"
            for e in rows:
                out += f"• **{e.title}** — {e.date} at {e.time} ({e.duration_minutes} min)\n"
                out += f"   👥 {e.attendees or 'No attendees'}\n"
                out += f"   📍 {e.location or 'No location'}\n"
                out += f"   🔗 {e.calendar_link or 'No link'}\n\n"
            return out

        elif any(w in q for w in ["email", "mail", "sent"]):
            rows = get_sent_emails(db, 10)
            if not rows:
                return "📭 No sent emails found in your database."
            out = "📧 YOUR SENT EMAILS:\n\n"
            for e in rows:
                out += f"• **{e.subject}**\n"
                out += f"   → To: {e.to_emails}\n"
                out += f"   Status: {e.status}\n\n"
            return out

        elif any(w in q for w in ["research", "market", "trend"]):
            rows = get_research_history(db, 10)
            if not rows:
                return "📭 No past research found in your database."
            out = "🔍 YOUR PAST RESEARCH:\n\n"
            for r in rows:
                out += f"• **{r.query[:100]}**\n\n"
            return out

        elif any(w in q for w in ["meeting", "summary", "transcript"]):
            rows = get_meeting_history(db, 10)
            if not rows:
                return "📭 No past meetings found in your database."
            out = "📋 YOUR PAST MEETINGS:\n\n"
            for m in rows:
                out += f"• **{m.query[:100]}**\n\n"
            return out

        elif any(w in q for w in ["file", "upload", "pdf", "document"]):
            rows = get_uploaded_files(db, 10)
            if not rows:
                return "📭 No uploaded files found in your database."
            out = "📄 YOUR UPLOADED FILES:\n\n"
            for f in rows:
                out += f"• **{f.filename}**\n"
                out += f"   Query: {f.query[:80] or 'No instructions'}\n\n"
            return out

        elif any(w in q for w in ["chat", "conversation", "history"]):
            rows = get_chat_history(db, 10)
            if not rows:
                return "📭 No chat history found."
            out = "💬 RECENT CHATS:\n\n"
            for c in rows:
                emoji = "👤" if c.role == "user" else "🤖"
                out += f"{emoji} [{c.intent or 'chat'}] {c.content[:100]}...\n\n"
            return out

        else:
            # Summary of everything
            chats = len(get_chat_history(db, 500))
            events = len(get_scheduled_events(db, 500))
            emails = len(get_sent_emails(db, 500))
            research = len(get_research_history(db, 500))
            meetings = len(get_meeting_history(db, 500))
            files = len(get_uploaded_files(db, 500))
            return (f"🗄️ DATABASE SUMMARY:\n\n"
                    f"• 💬 Chat messages: **{chats}**\n"
                    f"• 📅 Scheduled events: **{events}**\n"
                    f"• 📧 Sent emails: **{emails}**\n"
                    f"• 🔍 Research queries: **{research}**\n"
                    f"• 📋 Meeting analyses: **{meetings}**\n"
                    f"• 📄 Uploaded files: **{files}**\n\n"
                    f"Ask me to show any of these:\n"
                    f'  - "Show my scheduled events"\n'
                    f'  - "Show my sent emails"\n'
                    f'  - "Show my past research"\n'
                    f'  - "Show my uploaded files"')


def general_chat(user_input: str) -> str:
    """Handle general questions that don't fit any specific agent"""
    prompt = f"""You are an Enterprise AI Assistant. Answer the user's question helpfully and concisely.

If the user seems to want a specific feature, guide them:
- Meeting summaries → "Paste your meeting transcript and I'll summarize it"
- Document analysis → "Upload a PDF using the 📎 button"
- Business research → "Ask me to research any topic"
- Scheduling → "Tell me who, when, and what to schedule"
- Emails → "Tell me who to email and what to say"
- History/Database → "Ask me to show your scheduled events, emails, or research"

USER: {user_input}"""

    return call_gemini(prompt)