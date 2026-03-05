"""Standardized output schema and shared prompts for all image recognition approaches."""
from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Any
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .metadata import ImageMetadata


# ---------------------------------------------------------------------------
# Shared system prompt — identical across all direct vision approaches
# (GPT Vision Direct, Gemini Vision) for fair model comparison.
# Do NOT duplicate this in individual approach files.
# ---------------------------------------------------------------------------
VISION_SYSTEM_PROMPT = """You are an expert visual analyst specializing in identifying locations, landmarks, buildings, artworks, and cultural heritage sites from photographs.

Your task is to analyze the provided image and produce a structured identification in JSON format.

## Analysis instructions

**Description**: Provide a comprehensive qualitative description of everything visually observable in the image — architecture, style, materials, setting, lighting, surroundings, notable features.

**Photographer location**: Estimate where the photographer was physically standing when taking the photo. You may provide zero, one, or multiple guesses at different levels of specificity (e.g., both a specific courtyard and the broader city). Assign a confidence score to each.

**Subject location**: Estimate where the depicted subject is located. This may differ from the photographer's position (for example, when photographing a building from across a street, or using a telephoto lens). Again, zero to multiple guesses with confidence scores.

**Entities**: List every specific, identifiable thing you can observe — named landmarks, buildings, monuments, artworks, architectural styles, cultural sites, infrastructure, etc. For the same physical thing, you may include multiple entries at different specificity levels (e.g., a general style AND a specific named work). For artworks, include creator and period in the notes field if known. Include entities you are uncertain about with a lower confidence score rather than omitting them.

## Context interpretation

If GPS coordinates or a location name is provided, this tells you where the **photographer** was standing — NOT necessarily what is depicted. The photographer may be looking at something far away or using a zoom lens.

If a list of nearby places is provided, treat it as supporting context. These are places within 2 km of where the photo was taken. They may or may not be what is depicted in the image.

## Output format

Respond with a JSON object with exactly this structure:

{
  "description": "...",
  "photographer_location": [{"name": "...", "confidence": 0.85}],
  "subject_location": [{"name": "...", "confidence": 0.85}],
  "entities": [{"name": "...", "type": "landmark", "confidence": 0.85, "notes": null}]
}

Allowed entity types: landmark, building, monument, artwork, architectural_style, cultural_site, natural_feature, religious_site, public_space, infrastructure, transport_hub, viewpoint, district, signage, other

No preamble. Only the JSON."""

def build_vision_user_prompt(metadata: "ImageMetadata | None") -> str:
    """
    Build the shared user prompt for direct vision approaches (GPT Direct, Gemini).

    Identical output for all models — ensures fair comparison.
    """
    prompt = "Identify and describe what is shown in this image."

    if metadata:
        if metadata.location_info:
            loc = metadata.location_info
            # Prefer short "City, Country" to reduce tokens
            if loc.city and loc.country:
                addr = f"{loc.city}, {loc.country}"
            else:
                addr = loc.formatted_address or (
                    f"{metadata.gps_latitude:.6f}, {metadata.gps_longitude:.6f}"
                    if metadata.gps_latitude is not None
                    else None
                )
            if addr:
                prompt += f"\n\nPhotographer location context: {addr}"
        elif metadata.gps_latitude is not None and metadata.gps_longitude is not None:
            prompt += (
                f"\n\nPhotographer GPS coordinates: "
                f"{metadata.gps_latitude:.6f}, {metadata.gps_longitude:.6f}"
            )

        nearby = getattr(metadata, "nearby_places", None)
        if nearby:
            lines = [
                f"- {p.name} ({p.type.replace('_', ' ')}, {p.distance_meters}m)"
                for p in nearby
            ]
            prompt += "\n\nNearby places within 2 km:\n" + "\n".join(lines)

    prompt += (
        "\n\nFocus on specific identifiable subjects. "
        "Ignore generic scene elements unless they help identify the subject or location."
    )
    return prompt


def clean_json_response(text: str) -> str:
    """
    Strip markdown code fences from a model response before JSON parsing.

    Some models wrap their JSON in ```json ... ``` or ``` ... ``` blocks
    even when instructed not to. This removes such wrappers defensively.
    """
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        # Remove closing fence
        if text.endswith("```"):
            text = text[:-3].rstrip()
    return text


class EntityType(str, Enum):
    LANDMARK = "landmark"                       # Famous named places
    BUILDING = "building"                       # Specific named buildings
    MONUMENT = "monument"                       # Statues, memorials, columns, fountains
    ARTWORK = "artwork"                         # Paintings, sculptures, installations
    ARCHITECTURAL_STYLE = "architectural_style" # Gothic, Baroque, Art Nouveau, etc.
    CULTURAL_SITE = "cultural_site"             # UNESCO sites, heritage areas, historic districts
    NATURAL_FEATURE = "natural_feature"         # Mountains, rivers, parks, geological features
    RELIGIOUS_SITE = "religious_site"           # Churches, mosques, temples (when not specifically named)
    PUBLIC_SPACE = "public_space"               # Plazas, squares, promenades, courtyards
    INFRASTRUCTURE = "infrastructure"           # Bridges, towers, industrial structures, walls
    TRANSPORT_HUB = "transport_hub"             # Train stations, airports, metro stations
    VIEWPOINT = "viewpoint"                     # Scenic overlooks, observation points, hilltops
    DISTRICT = "district"                       # Neighborhoods, historic quarters, city areas
    SIGNAGE = "signage"                         # Text detected via OCR on signs, plaques, inscriptions
    OTHER = "other"                             # Anything that doesn't fit the above categories


class LocationGuess(BaseModel):
    name: str = Field(description="Place name at any level of specificity")
    confidence: float = Field(description="Confidence score from 0.0 (uncertain) to 1.0 (certain)")


class Entity(BaseModel):
    name: str = Field(description="Name of the identified thing")
    type: EntityType = Field(description="Standardized category of this entity")
    confidence: float = Field(description="Confidence score from 0.0 (uncertain) to 1.0 (certain)")
    notes: str | None = Field(default=None, description="Relevant details: artist, date, style, materials, etc.")


class RecognitionOutput(BaseModel):
    """Structured output produced by all AI vision models."""
    description: str = Field(description="Comprehensive qualitative description of everything observable in the image")
    photographer_location: list[LocationGuess] = Field(
        default_factory=list,
        description="Where the photographer was physically standing. Provide 0 or more guesses, can include same place at different specificity levels."
    )
    subject_location: list[LocationGuess] = Field(
        default_factory=list,
        description="Where the depicted subject is located. May differ from photographer location (e.g., photographing a building from across the street). Provide 0 or more guesses."
    )
    entities: list[Entity] = Field(
        default_factory=list,
        description="All specific identifiable things in the image. Include the same thing at multiple specificity levels if appropriate. Prefer more entities with lower confidence over fewer with higher confidence."
    )


def build_full_record(
    approach_name: str,
    model_id: str,
    metadata: "ImageMetadata | None",
    user_prompt: str,
    ai_output: RecognitionOutput,
    processing_time_ms: int = 0,
) -> dict[str, Any]:
    """
    Assemble the standard full output record from an AI vision model result.

    This function is used by all AI-based approaches (GPT, Gemini) to produce
    a consistent output structure for the details field of RecognitionResult.

    Args:
        approach_name: Human-readable name of the recognition approach.
        model_id: Model identifier string (e.g., 'gpt-4o', 'gemini-2.0-flash').
        metadata: Optional image metadata with GPS and location info.
        user_prompt: The full user prompt text that was sent to the model.
        ai_output: Validated RecognitionOutput parsed from the model response.
        processing_time_ms: Total processing time in milliseconds.

    Returns:
        Dict suitable for use as RecognitionResult.details.
    """
    record: dict[str, Any] = {
        "approach": approach_name,
        "model": model_id,
        "processing_time_ms": processing_time_ms,
        "geocoding_time_ms": None,
        "nearby_places_time_ms": None,
        "gps_coordinates": None,
        "reverse_geocoding": None,
        "nearby_places": [],
        "input_prompt": None,  # Prompt is backend-generated; omitted to reduce payload
        "description": ai_output.description,
        "photographer_location": [
            {"name": g.name, "confidence": g.confidence}
            for g in ai_output.photographer_location
        ],
        "subject_location": [
            {"name": g.name, "confidence": g.confidence}
            for g in ai_output.subject_location
        ],
        "entities": [
            {
                "name": e.name,
                "type": e.type.value,
                "confidence": e.confidence,
                "notes": e.notes,
            }
            for e in ai_output.entities
        ],
    }

    if metadata is not None:
        record["geocoding_time_ms"] = metadata.geocoding_time_ms
        record["nearby_places_time_ms"] = metadata.nearby_places_time_ms

        if metadata.gps_latitude is not None and metadata.gps_longitude is not None:
            record["gps_coordinates"] = {
                "latitude": metadata.gps_latitude,
                "longitude": metadata.gps_longitude,
            }

        if metadata.location_info is not None:
            loc = metadata.location_info
            record["reverse_geocoding"] = {
                "formatted_address": loc.formatted_address,
                "city": loc.city,
                "county": loc.county,
                "country": loc.country,
            }

        nearby = getattr(metadata, "nearby_places", None)
        if nearby:
            record["nearby_places"] = [
                {
                    "name": p.name,
                    "type": p.type,
                    "distance_meters": p.distance_meters,
                    "rating": p.rating,
                    "vicinity": p.vicinity,
                }
                for p in nearby
            ]

    return record


def extract_primary(ai_output: RecognitionOutput) -> tuple[str | None, float | None]:
    """
    Extract the primary identification and confidence from a RecognitionOutput.

    Prefers the highest-confidence entity; falls back to highest-confidence
    subject_location guess if no entities are present.

    Args:
        ai_output: Validated RecognitionOutput from a vision model.

    Returns:
        Tuple of (identified_name, confidence). Both may be None if output is empty.
    """
    if ai_output.entities:
        top = max(ai_output.entities, key=lambda e: e.confidence)
        return top.name, top.confidence
    if ai_output.subject_location:
        top = max(ai_output.subject_location, key=lambda g: g.confidence)
        return top.name, top.confidence
    return None, None
