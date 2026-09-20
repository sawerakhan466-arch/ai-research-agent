from crewai.tools import tool
from ddgs import DDGS


@tool("DuckDuckGo Search")
def search_web(query: str) -> str:
    """Search the web using DuckDuckGo.
    Input must be a short search query string.
    Returns titles, links and short snippets of the top results."""
    try:
        results = DDGS().text(query, max_results=5)
    except Exception as e:
        return f"Search failed: {e}"

    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, start=1):
        snippet = r.get("body", "")[:300]  # keep it short to save tokens
        lines.append(f"{i}. {r.get('title')}\n   URL: {r.get('href')}\n   Snippet: {snippet}")
    return "\n\n".join(lines)
