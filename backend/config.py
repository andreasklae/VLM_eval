"""Configuration for image recognition approaches."""

import logging
import os
from functools import lru_cache
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """Image recognition settings from environment variables."""

    # Azure OpenAI
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment: str        # strong model deployment (e.g. gpt-5)
    azure_openai_deployment_fast: str   # fast model deployment (e.g. gpt-5-nano)
    azure_openai_api_version: str

    # Google Cloud Vision (requires service account JSON file)
    google_credentials_path: str

    # Google Custom Search API (alternative to Bing)
    google_api_key: str
    google_search_engine_id: str

    # OpenAI Direct API (for Agents SDK web search)
    openai_direct_api_key: str

    # Google Maps Places API
    google_maps_api_key: str

    # Google Gemini (Google AI Studio)
    gemini_api_key: str
    gemini_model_fast: str
    gemini_model_strong: str

    @property
    def use_azure_openai(self) -> bool:
        """Azure OpenAI is configured (endpoint + key)."""
        return bool(self.azure_openai_endpoint) and bool(self.azure_openai_api_key)

    @property
    def use_direct_openai(self) -> bool:
        """Direct OpenAI key is set (fallback when Azure not configured)."""
        return bool(self.openai_direct_api_key)

    def use_direct_openai_for_vision(self, has_metadata_enrichment: bool = False) -> bool:
        """Use direct OpenAI for vision when the direct API key is set (all requests, with or without metadata)."""
        return bool(self.openai_direct_api_key)

    def use_azure_openai_for_vision(self, has_metadata_enrichment: bool = False) -> bool:
        """Use Azure for vision only when direct OpenAI is not configured."""
        return (not self.use_direct_openai_for_vision(has_metadata_enrichment)) and self.use_azure_openai

    @property
    def gpt_vision_available(self) -> bool:
        """Check if GPT Vision is available (Azure or direct OpenAI)."""
        return self.use_azure_openai or self.use_direct_openai

    @property
    def google_vision_available(self) -> bool:
        """Check if Google Cloud Vision is available."""
        return bool(self.google_credentials_path) and os.path.exists(
            self.google_credentials_path
        )

    @property
    def google_search_available(self) -> bool:
        """Check if Google Custom Search is available."""
        return bool(self.google_api_key) and bool(self.google_search_engine_id)

    @property
    def openai_web_search_available(self) -> bool:
        """Check if OpenAI Agents SDK web search is available."""
        return bool(self.openai_direct_api_key)

    @property
    def google_maps_places_available(self) -> bool:
        """Check if Google Maps Places API is available."""
        return bool(self.google_maps_api_key)

    @property
    def gemini_available(self) -> bool:
        """Check if Google Gemini API is available."""
        return bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    """Get settings from environment variables."""
    return Settings(
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5"),
        azure_openai_deployment_fast=os.getenv("AZURE_OPENAI_DEPLOYMENT_FAST", "gpt-5-nano"),
        azure_openai_api_version=os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-08-01-preview"
        ),
        google_credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        google_search_engine_id=os.getenv("GOOGLE_SEARCH_ENGINE_ID", ""),
        openai_direct_api_key=os.getenv("OPENAI_DIRECT_API_KEY", ""),
        google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        # Gemini 3 series: image understanding + structured JSON output supported
        gemini_model_fast=os.getenv("GEMINI_MODEL_FAST", "gemini-3-flash-preview"),
        gemini_model_strong=os.getenv("GEMINI_MODEL_STRONG", "gemini-3-pro-preview"),
    )


def validate_config_at_startup() -> None:
    """Log configuration status at startup.

    Reports which recognition approaches are available and which are
    missing credentials.  This runs once when the server starts so
    operators see misconfigurations immediately in the log rather than
    discovering them mid-request.
    """
    settings = get_settings()

    # Approach availability checks, ordered by priority
    checks: list[tuple[str, bool, str]] = [
        (
            "GPT Vision (Direct OpenAI)",
            settings.use_direct_openai,
            "Set OPENAI_DIRECT_API_KEY",
        ),
        (
            "GPT Vision (Azure OpenAI)",
            settings.use_azure_openai,
            "Set AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY",
        ),
        (
            "Gemini Vision",
            settings.gemini_available,
            "Set GEMINI_API_KEY",
        ),
        (
            "Google Cloud Vision",
            settings.google_vision_available,
            "Set GOOGLE_APPLICATION_CREDENTIALS to a valid service account JSON",
        ),
        (
            "Google Maps Places (GPS enrichment)",
            settings.google_maps_places_available,
            "Set GOOGLE_MAPS_API_KEY",
        ),
        (
            "Google Custom Search (search backend)",
            settings.google_search_available,
            "Set GOOGLE_API_KEY + GOOGLE_SEARCH_ENGINE_ID",
        ),
        (
            "OpenAI Web Search (search backend)",
            settings.openai_web_search_available,
            "Set OPENAI_DIRECT_API_KEY",
        ),
    ]

    available_count = 0
    for name, is_ok, hint in checks:
        if is_ok:
            logger.info("  [OK]      %s", name)
            available_count += 1
        else:
            logger.warning("  [MISSING] %s -- %s", name, hint)

    if available_count == 0:
        logger.error(
            "No recognition approaches are available. "
            "The server will start but all /recognize requests will fail. "
            "Configure at least one vision API key."
        )
    else:
        logger.info("%d/%d approach groups configured", available_count, len(checks))
