from tavily import TavilyClient
from Backend.config.settings import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)


def search(query: str, max_results: int = 5) -> dict:
    """Search the web using Tavily and return structured results"""
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True,
        include_raw_content=False,
    )
    return response


def format_search_results(response: dict) -> str:
    """Convert Tavily response into readable text for Gemini"""
    output = ""

    # Include Tavily's direct answer if available
    if response.get("answer"):
        output += f"DIRECT ANSWER:\n{response['answer']}\n\n"

    # Include individual search results
    output += "SEARCH RESULTS:\n"
    for i, result in enumerate(response.get("results", []), 1):
        output += f"\n--- Result {i} ---\n"
        output += f"Title: {result.get('title', 'N/A')}\n"
        output += f"URL: {result.get('url', 'N/A')}\n"
        output += f"Content: {result.get('content', 'N/A')}\n"

    return output