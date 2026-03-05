"""
Multi-approach image recognition system.

Provides parallel landmark/artwork identification using:
1. GPT Vision Direct (strong/fast) - Azure OpenAI or OpenAI gpt-4o / gpt-4o-mini
2. GPT Vision + Search (strong/fast) - Visual description + conditional Wikipedia/web search
3. Gemini Vision (strong/fast) - Google Gemini via Google AI Studio
4. Google Cloud Vision - Landmark detection, web detection, OCR
5. Google Maps Places - GPS-based nearby place lookup (runs last)

All AI-based approaches produce a standardized RecognitionOutput schema
(see schema.py) in their details field.
"""

from .base import ImageRecognitionApproach, RecognitionResult, normalize_details
from .runner import recognize_image, get_available_approaches, get_all_approaches
from .schema import RecognitionOutput, Entity, EntityType, LocationGuess

__all__ = [
    # Base classes
    "ImageRecognitionApproach",
    "RecognitionResult",
    "normalize_details",
    # Runner
    "recognize_image",
    "get_available_approaches",
    "get_all_approaches",
    # Schema
    "RecognitionOutput",
    "Entity",
    "EntityType",
    "LocationGuess",
]
