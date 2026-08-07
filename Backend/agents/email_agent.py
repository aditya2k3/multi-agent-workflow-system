import json
import asyncio
from Backend.services.gemini_service import call_gemini
from Backend.services.gmail_service import send_draft_email, get_recent_emails
from Backend.prompts.email_prompt import (
    EMAIL_SYSTEM_PROMPT,
    DRAFT_EMAIL_PROMPT,
    REPLY_EMAIL_PROMPT,
    FOLLOWUP_EMAIL_PROMPT,
)
from Backend.tools.agent_tools import tool_send_email


def parse_email_json(response: str) -> dict:
    """Extract JSON from Gemini response"""
    try:
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
        return {"error": str(e), "raw_response": response}


def save_to_db(recipients, subject, body):
    """Save email to database in background"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tool_send_email(
            to=recipients,
            subject=subject,
            body=body,
        ))
        loop.close()
    except Exception:
        pass  # Don't fail if DB save fails


def draft_email(user_input: str) -> str:
    """Draft an email from natural language instructions"""
    prompt = DRAFT_EMAIL_PROMPT.format(
        system_prompt=EMAIL_SYSTEM_PROMPT,
        user_input=user_input,
    )

    response = call_gemini(prompt)
    email_data = parse_email_json(response)

    if "error" in email_data:
        return f"⚠️ Could not draft email: {email_data['error']}\n\nRaw: {email_data.get('raw_response', '')}"

    recipients = email_data.get("to", [])

    result = f"""📧 EMAIL DRAFTED

📌 Subject: {email_data.get('subject', 'N/A')}
🎭 Tone: {email_data.get('tone', 'N/A')}
👥 To: {', '.join(recipients) if recipients else 'Not specified'}
📋 CC: {', '.join(email_data.get('cc', [])) or 'None'}

📝 BODY:
{email_data.get('body', 'N/A')}"""

    # Auto-send if recipients exist
    if recipients:
        try:
            send_result = send_draft_email(
                to=recipients,
                subject=email_data.get("subject", "No Subject"),
                body=email_data.get("body", ""),
                cc=email_data.get("cc", []),
            )
            result += f"\n\n✅ EMAIL SENT successfully to: {', '.join(send_result['to'])}"
            result += f"\n📨 Message ID: {send_result['message_id']}"

            # ✅ SAVE TO DATABASE AFTER SEND
            save_to_db(
                recipients,
                email_data.get("subject", "No Subject"),
                email_data.get("body", ""),
            )

        except Exception as e:
            result += f"\n\n⚠️ Failed to send: {str(e)}"
            result += "\n📋 Copy the body above and send manually."
    else:
        result += "\n\nℹ️ No recipients detected. Provide email addresses to send automatically."

    return result


def reply_to_email(sender: str, subject: str, content: str, reply_instructions: str) -> str:
    """Draft a reply to an existing email"""
    prompt = REPLY_EMAIL_PROMPT.format(
        system_prompt=EMAIL_SYSTEM_PROMPT,
        sender=sender,
        subject=subject,
        content=content,
        reply_instructions=reply_instructions,
    )

    response = call_gemini(prompt)
    email_data = parse_email_json(response)

    if "error" in email_data:
        return f"⚠️ Could not draft reply: {email_data['error']}"

    result = f"""📧 REPLY DRAFTED

📌 Subject: {email_data.get('subject', 'N/A')}
🎭 Tone: {email_data.get('tone', 'N/A')}

📝 REPLY BODY:
{email_data.get('body', 'N/A')}"""

    sender_email = sender.split("<")[-1].replace(">", "").strip() if "<" in sender else sender.strip()

    if sender_email and "@" in sender_email:
        try:
            send_result = send_draft_email(
                to=[sender_email],
                subject=email_data.get("subject", f"Re: {subject}"),
                body=email_data.get("body", ""),
            )
            result += f"\n\n✅ REPLY SENT to: {sender_email}"

            # ✅ SAVE TO DATABASE
            save_to_db(
                [sender_email],
                email_data.get("subject", f"Re: {subject}"),
                email_data.get("body", ""),
            )

        except Exception as e:
            result += f"\n\n⚠️ Failed to send reply: {str(e)}"

    return result


def draft_followup(context: str, days: int = 3) -> str:
    """Draft a polite follow-up email"""
    prompt = FOLLOWUP_EMAIL_PROMPT.format(
        system_prompt=EMAIL_SYSTEM_PROMPT,
        context=context,
        days=days,
    )

    response = call_gemini(prompt)
    email_data = parse_email_json(response)

    if "error" in email_data:
        return f"⚠️ Could not draft follow-up: {email_data['error']}"

    return f"""📧 FOLLOW-UP DRAFTED

📌 Subject: {email_data.get('subject', 'N/A')}

📝 BODY:
{email_data.get('body', 'N/A')}"""


def get_inbox_summary(max_emails: int = 5) -> str:
    """Fetch and summarize recent emails"""
    try:
        emails = get_recent_emails(max_results=max_emails)
    except Exception as e:
        return f"⚠️ Could not fetch emails: {str(e)}"

    if not emails:
        return "📭 Your inbox is empty or no emails matched."

    summary = "📬 RECENT EMAILS:\n\n"
    for i, email in enumerate(emails, 1):
        summary += f"**{i}. {email['subject']}**\n"
        summary += f"   From: {email['from']}\n"
        summary += f"   Date: {email['date']}\n"
        summary += f"   Preview: {email['snippet'][:100]}...\n\n"

    return summary


def auto_route(query: str) -> str:
    """Auto-detect what the user wants"""
    query_lower = query.lower()

    if any(word in query_lower for word in ["inbox", "recent emails", "show emails", "fetch"]):
        return get_inbox_summary()
    elif any(word in query_lower for word in ["follow up", "follow-up", "reminder"]):
        return draft_followup(query)
    elif any(word in query_lower for word in ["reply", "respond"]):
        return "⚠️ To reply to a specific email, use the format:\n\nReply to [sender] about [subject]: [your instructions]\n\nOr provide the email content directly."
    else:
        return draft_email(query)


def run_email_agent(query: str, task: str = "auto") -> str:
    """Main entry point called by API layer"""
    task = task.lower().strip()

    if task == "draft":
        return draft_email(query)
    elif task == "followup":
        return draft_followup(query)
    elif task == "inbox":
        return get_inbox_summary()
    elif task == "send":
        return direct_send(query)
    else:
        return auto_route(query)


def direct_send(query: str) -> str:
    """Parse a direct send command and send immediately"""
    import re

    to_match = re.search(r'to[:\s]+([^\s,]+(?:,\s*[^\s,]+)*)', query, re.IGNORECASE)
    subject_match = re.search(r'subject[:\s]+(.+?)(?:\s+body[:\s]|$)', query, re.IGNORECASE)
    body_match = re.search(r'body[:\s]+(.+)', query, re.IGNORECASE | re.DOTALL)

    if not to_match or not body_match:
        return draft_email(query)

    recipients = [e.strip() for e in to_match.group(1).split(",")]
    subject = subject_match.group(1).strip() if subject_match else "No Subject"
    body = body_match.group(1).strip()

    try:
        result = send_draft_email(to=recipients, subject=subject, body=body)

        # ✅ SAVE TO DATABASE
        save_to_db(recipients, subject, body)

        return f"✅ Email sent to: {', '.join(result['to'])}\n📌 Subject: {subject}"
    except Exception as e:
        return f"⚠️ Failed to send: {str(e)}"