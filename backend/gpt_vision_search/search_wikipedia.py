"""Wikipedia search backend for landmark identification."""

import logging
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WikipediaSearchResult:
    """Result from Wikipedia search."""

    title: str
    snippet: str
    url: str
    score: float  # Relevance score (position-based)


async def search_wikipedia(
    query: str,
    language: str = "en",
    limit: int = 5,
) -> list[WikipediaSearchResult]:
    """
    Search Wikipedia for articles matching the query.

    Args:
        query: Search query (e.g., description of a landmark).
        language: Wikipedia language code (default: en).
        limit: Maximum number of results.

    Returns:
        List of WikipediaSearchResult.
    """
    base_url = f"https://{language}.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json",
        "srprop": "snippet|titlesnippet",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

    # Validate response structure
    if not isinstance(data, dict):
        logger.warning("Wikipedia API returned non-dict response: %s", type(data).__name__)
        return []

    # Check for MediaWiki API errors
    if "error" in data:
        error_info = data["error"].get("info", "unknown") if isinstance(data["error"], dict) else str(data["error"])
        logger.warning("Wikipedia API error: %s", error_info)
        return []

    query_data = data.get("query")
    if not isinstance(query_data, dict):
        logger.warning("Wikipedia API response missing 'query' key")
        return []

    results = []
    search_results = query_data.get("search", [])
    if not isinstance(search_results, list):
        logger.warning("Wikipedia search results is not a list: %s", type(search_results).__name__)
        return []

    for i, item in enumerate(search_results):
        # Score based on position (higher = better)
        score = 1.0 - (i * 0.15)  # First result = 1.0, second = 0.85, etc.

        results.append(
            WikipediaSearchResult(
                title=item.get("title", ""),
                snippet=item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                url=f"https://{language}.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                score=max(0.1, score),
            )
        )

    return results


async def get_wikipedia_summary(title: str, language: str = "en") -> str | None:
    """
    Get the summary/extract of a Wikipedia article.

    Args:
        title: Article title.
        language: Wikipedia language code.

    Returns:
        Article summary or None if not found.
    """
    base_url = f"https://{language}.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

    if not isinstance(data, dict):
        logger.warning("Wikipedia summary API returned non-dict response")
        return None

    query_data = data.get("query")
    if not isinstance(query_data, dict):
        return None

    pages = query_data.get("pages", {})
    if not isinstance(pages, dict):
        return None

    for page in pages.values():
        if isinstance(page, dict) and "extract" in page:
            return page["extract"]

    return None
