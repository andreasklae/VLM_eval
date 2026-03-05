"""Google Custom Search backend for landmark identification."""

import logging
import httpx
from dataclasses import dataclass

from ..config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class GoogleSearchResult:
    """Result from Google Custom Search."""

    title: str
    snippet: str
    url: str
    score: float  # Relevance score (position-based)


def is_available() -> bool:
    """Check if Google Custom Search is available."""
    return get_settings().google_search_available


async def search_google(
    query: str,
    limit: int = 5,
) -> list[GoogleSearchResult]:
    """
    Search Google for pages matching the query using Custom Search API.

    Args:
        query: Search query (e.g., description of a landmark).
        limit: Maximum number of results (max 10 per request).

    Returns:
        List of GoogleSearchResult.
    """
    settings = get_settings()

    if not settings.google_search_available:
        return []

    endpoint = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": settings.google_api_key,
        "cx": settings.google_search_engine_id,
        "q": query,
        "num": min(limit, 10),  # API max is 10
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

    # Validate response structure
    if not isinstance(data, dict):
        logger.warning("Google Custom Search returned non-dict response: %s", type(data).__name__)
        return []

    # Check for API error
    if "error" in data:
        error_msg = data["error"].get("message", "unknown") if isinstance(data["error"], dict) else str(data["error"])
        logger.warning("Google Custom Search API error: %s", error_msg)
        return []

    results = []
    items = data.get("items", [])
    if not isinstance(items, list):
        logger.warning("Google Custom Search 'items' is not a list: %s", type(items).__name__)
        return []

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        # Score based on position
        score = 1.0 - (i * 0.1)

        results.append(
            GoogleSearchResult(
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                url=item.get("link", ""),
                score=max(0.1, score),
            )
        )

    logger.info("Google Custom Search returned %d results for query: %s", len(results), query[:80])
    return results
