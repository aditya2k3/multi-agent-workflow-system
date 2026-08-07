from Backend.services.gemini_service import call_gemini
from Backend.prompts.meeting_prompt import (
    MEETING_SYSTEM_PROMPT,
    SUMMARY_PROMPT,
    ACTION_ITEMS_PROMPT,
    FOLLOWUP_EMAIL_PROMPT,
    ANALYSIS_PROMPT,
)


def summarize_meeting(transcript: str) -> str:
    prompt = SUMMARY_PROMPT.format(
        system_prompt=MEETING_SYSTEM_PROMPT,
        transcript=transcript,
    )
    return call_gemini(prompt)


def extract_action_items(transcript: str) -> str:
    prompt = ACTION_ITEMS_PROMPT.format(
        system_prompt=MEETING_SYSTEM_PROMPT,
        transcript=transcript,
    )
    return call_gemini(prompt)


def draft_followup_email(transcript: str, recipients: str = "all attendees") -> str:
    prompt = FOLLOWUP_EMAIL_PROMPT.format(
        system_prompt=MEETING_SYSTEM_PROMPT,
        transcript=transcript,
        recipients=recipients,
    )
    return call_gemini(prompt)


def analyze_meeting(transcript: str) -> str:
    prompt = ANALYSIS_PROMPT.format(
        system_prompt=MEETING_SYSTEM_PROMPT,
        transcript=transcript,
    )
    return call_gemini(prompt)


def auto_route(query: str) -> str:
    query_lower = query.lower()

    if any(word in query_lower for word in ["action item", "task", "todo", "to-do"]):
        return extract_action_items(query)
    elif any(word in query_lower for word in ["email", "follow up", "follow-up"]):
        return draft_followup_email(query)
    elif any(word in query_lower for word in ["summarize", "summary", "brief"]):
        return summarize_meeting(query)
    else:
        return analyze_meeting(query)


def run_meeting_agent(query: str, task: str = "auto") -> str:
    task = task.lower().strip()

    if task == "summarize":
        return summarize_meeting(query)
    elif task == "action_items":
        return extract_action_items(query)
    elif task == "followup_email":
        return draft_followup_email(query)
    elif task == "analyze":
        return analyze_meeting(query)
    else:
        return auto_route(query)