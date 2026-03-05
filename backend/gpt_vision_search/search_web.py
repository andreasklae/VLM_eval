"""Web search backend using OpenAI Agents SDK WebSearchTool."""

import logging
from dataclasses import dataclass

from openai import AsyncOpenAI

from ..config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class WebSearchResult:
    """Result from web search."""

    title: str
    snippet: str
    url: str
    score: float  # Position-based relevance score


def is_available() -> bool:
    """Check if web search is available (requires direct OpenAI API key)."""
    return get_settings().openai_web_search_available


async def search_web(
    query: str,
    limit: int = 5,
) -> list[WebSearchResult]:
    """
    Search the web using OpenAI Agents SDK WebSearchTool.

    Args:
        query: Search query (e.g., description of a landmark).
        limit: Maximum number of results.

    Returns:
        List of WebSearchResult.
    """
    settings = get_settings()

    if not settings.openai_web_search_available:
        return []

    # Import here to avoid requiring openai-agents if not using web search
    from agents import Agent, Runner
    from agents.tool import WebSearchTool

    # Create a simple agent with web search capability
    agent = Agent(
        name="web_searcher",
        instructions=f"""You are a web search assistant. Search for information about visual content, including landmarks, buildings, artworks, paintings, statues, viewpoints, and any other notable subjects.

When given a query, use web search to find relevant results. Return the top {limit} most relevant results.

For each result, extract:
- title: The page title
- snippet: A brief description or excerpt
- url: The page URL

Format your response as a simple list of results.""",
        tools=[WebSearchTool()],
        model="gpt-4o-mini",  # Use mini for cost efficiency
    )

    # Pass API key via OpenAIProvider to avoid mutating os.environ,
    # which causes race conditions under concurrent load.
    try:
        from agents import OpenAIProvider
        from agents.run import RunConfig

        provider = OpenAIProvider(api_key=settings.openai_direct_api_key)
        logger.info("Running web search for query: %s", query[:100])

        result = await Runner.run(
            agent,
            f"Search for: {query}. Return the top {limit} results with title, snippet, and URL.",
            run_config=RunConfig(model_provider=provider),
        )

        # Parse results from agent response
        results = _parse_agent_response(result.final_output, limit)
        logger.info("Web search returned %d results", len(results))
        return results

    except Exception as e:
        logger.error("Web search failed: %s", e, exc_info=True)
        return []


def _parse_agent_response(response: str, limit: int) -> list[WebSearchResult]:
    """Parse the agent's response into WebSearchResult objects."""
    results = []

    if not response:
        return results

    # Simple parsing - look for URLs and surrounding text
    import re

    # Try to find structured results (title, snippet, url patterns)
    lines = response.split('\n')
    current_title = ""
    current_snippet = ""
    current_url = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for URL
        url_match = re.search(r'https?://[^\s\)]+', line)
        if url_match:
            current_url = url_match.group(0).rstrip('.,;:')

            # If we have a URL, try to extract title from the line
            if not current_title:
                # Remove the URL and use rest as title
                title_part = re.sub(r'https?://[^\s\)]+', '', line).strip()
                title_part = re.sub(r'^[-*•\d.)\]]+\s*', '', title_part).strip()
                if title_part:
                    current_title = title_part[:200]

        # Check for title patterns
        elif line.startswith(('Title:', '**', '###', '##')):
            current_title = re.sub(r'^(Title:|[*#]+)\s*', '', line).strip()[:200]

        # Check for snippet patterns
        elif line.startswith(('Snippet:', 'Description:', '-')):
            current_snippet = re.sub(r'^(Snippet:|Description:|-)\s*', '', line).strip()[:500]

        # If we have enough info, create a result
        if current_url and (current_title or current_snippet):
            results.append(
                WebSearchResult(
                    title=current_title or current_url,
                    snippet=current_snippet or "",
                    url=current_url,
                    score=1.0 - (len(results) * 0.1),
                )
            )
            current_title = ""
            current_snippet = ""
            current_url = ""

            if len(results) >= limit:
                break

    # If no structured results found, try to extract any URLs
    if not results:
        urls = re.findall(r'https?://[^\s\)]+', response)
        for i, url in enumerate(urls[:limit]):
            results.append(
                WebSearchResult(
                    title=url,
                    snippet="",
                    url=url.rstrip('.,;:'),
                    score=1.0 - (i * 0.1),
                )
            )

    return results
