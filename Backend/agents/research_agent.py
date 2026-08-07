from Backend.services.tavily_service import search, format_search_results
from Backend.services.gemini_service import call_gemini
from Backend.prompts.research_prompt import (
    RESEARCH_SYSTEM_PROMPT,
    RESEARCH_PROMPT,
    QUICK_RESEARCH_PROMPT,
    COMPETITOR_ANALYSIS_PROMPT,
)


def deep_research(query: str) -> str:
    """Full research with detailed analysis"""
    # Step 1: Search the web
    search_response = search(query, max_results=5)

    # Step 2: Format results for Gemini
    search_results = format_search_results(search_response)

    # Step 3: Build prompt
    prompt = RESEARCH_PROMPT.format(
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        search_results=search_results,
        query=query,
    )

    # Step 4: Send to Gemini for analysis
    return call_gemini(prompt)


def quick_research(query: str) -> str:
    """Quick concise research"""
    search_response = search(query, max_results=3)
    search_results = format_search_results(search_response)

    prompt = QUICK_RESEARCH_PROMPT.format(
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        search_results=search_results,
        query=query,
    )

    return call_gemini(prompt)


def competitor_analysis(query: str) -> str:
    """Focused competitor analysis"""
    search_response = search(query, max_results=5)
    search_results = format_search_results(search_response)

    prompt = COMPETITOR_ANALYSIS_PROMPT.format(
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        search_results=search_results,
        query=query,
    )

    return call_gemini(prompt)


def auto_route(query: str) -> str:
    """Auto-detect what type of research the user wants"""
    query_lower = query.lower()

    if any(word in query_lower for word in ["competitor", "vs", "versus", "compare", "comparison"]):
        return competitor_analysis(query)
    elif any(word in query_lower for word in ["quick", "brief", "short", "fast"]):
        return quick_research(query)
    else:
        return deep_research(query)


def run_research_agent(query: str, task: str = "auto") -> str:
    """Main entry point called by API layer"""
    task = task.lower().strip()

    if task == "deep":
        return deep_research(query)
    elif task == "quick":
        return quick_research(query)
    elif task == "competitor":
        return competitor_analysis(query)
    else:
        return auto_route(query)