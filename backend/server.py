"""FastAPI server for image recognition."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load .env file if present
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Maximum image size in bytes (20 MB). Vision APIs have their own limits
# (OpenAI: 20 MB, Google Cloud Vision: 10 MB) but we enforce a single
# server-side limit to reject oversized uploads early, before base64
# encoding inflates the payload further.
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

load_dotenv(Path(__file__).parent / ".env")

# Set GOOGLE_APPLICATION_CREDENTIALS if Mimir_key.json exists
import os

mimir_key_path = Path(__file__).parent / "Mimir_key.json"
if mimir_key_path.exists():
    current_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not current_creds or not Path(current_creds).exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(mimir_key_path.resolve())

from .runner import get_all_approaches, recognize_image_bytes
from .base import RecognitionResult, normalize_details
from .config import validate_config_at_startup
from .metadata import (
    extract_metadata,
    ImageMetadata,
    categorize_nearby_places,
    NEARBY_PLACES_RADIUS_METERS,
)

app = FastAPI(
    title="Image Recognition API",
    description="API for identifying visual content in images using multiple approaches",
    version="1.0.0",
)


@app.on_event("startup")
async def _startup_validation() -> None:
    """Run configuration checks at server startup."""
    logger.info("Image Recognition API starting up -- checking configuration...")
    validate_config_at_startup()


class ApproachInfo(BaseModel):
    """Information about an approach."""

    name: str
    available: bool


class RecognitionResponse(BaseModel):
    """Response from recognition endpoint."""

    image_filename: str
    timestamp: str
    processing_time_seconds: float
    use_gps: bool
    metadata: dict[str, Any] | None = None
    google_maps_places: dict[str, Any] | None = None
    approaches: list[dict[str, Any]]


def result_to_dict(result: RecognitionResult) -> dict[str, Any]:
    """Convert RecognitionResult to dictionary for JSON serialization.

    Normalizes the ``details`` dict so all approaches expose a common
    set of keys, making downstream consumption consistent.
    """
    return {
        "approach": result.approach,
        "identified": result.identified,
        "confidence": result.confidence,
        "success": result.success,
        "error": result.error,
        "details": normalize_details(result.details),
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Image Recognition API",
        "version": "1.0.0",
        "endpoints": {
            "recognize": "POST /recognize - Recognize content in an uploaded image",
            "approaches": "GET /approaches - List available recognition approaches",
        },
    }


@app.get("/approaches", response_model=list[ApproachInfo])
async def list_approaches():
    """
    List all available recognition approaches and their availability status.

    Returns:
        List of approach information including name and availability.
    """
    all_approaches = get_all_approaches()
    return [
        ApproachInfo(name=approach.name, available=approach.is_available())
        for approach in all_approaches
    ]


@app.post("/recognize", response_model=RecognitionResponse)
async def recognize(
    image: UploadFile = File(..., description="Image file to recognize"),
    approaches: str | None = Query(
        None,
        description="Comma-separated list of approach names to use (e.g., 'GPT Vision Direct,Google Cloud Vision'). If not provided, all approaches will be used.",
    ),
    use_gps: bool = Query(
        True,
        description="Whether to extract and use GPS from EXIF (enables location and nearby places). Default: True.",
    ),
):
    """
    Recognize visual content in an uploaded image using specified approaches.

    Args:
        image: Image file to process (multipart/form-data)
        approaches: Optional comma-separated list of approach names to use.
                   If not provided, all available approaches will be used.
        use_gps: Whether to extract and use GPS from EXIF. Default: True.

    Returns:
        JSON response with recognition results from each approach.
    """
    start_time = datetime.now()

    # Read image data
    try:
        image_data = await image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {str(e)}")

    if not image_data:
        raise HTTPException(status_code=400, detail="Empty image file")

    # Enforce image size limit before base64 encoding / API submission
    if len(image_data) > MAX_IMAGE_SIZE_BYTES:
        size_mb = len(image_data) / (1024 * 1024)
        limit_mb = MAX_IMAGE_SIZE_BYTES / (1024 * 1024)
        logger.warning("Image too large: %.1f MB (limit: %.0f MB)", size_mb, limit_mb)
        raise HTTPException(
            status_code=413,
            detail=f"Image too large: {size_mb:.1f} MB. Maximum allowed size is {limit_mb:.0f} MB.",
        )

    # Detect MIME type
    mime_type = image.content_type
    if not mime_type or not mime_type.startswith("image/"):
        # Try to guess from filename
        from mimetypes import guess_type

        guessed_type, _ = guess_type(image.filename or "")
        if guessed_type and guessed_type.startswith("image/"):
            mime_type = guessed_type
        else:
            # Handle HEIC/HEIF explicitly as mimetypes may not recognize them
            if image.filename:
                ext_lower = image.filename.lower()
                if ext_lower.endswith(('.heic', '.heif')):
                    mime_type = "image/heic"
                else:
                    mime_type = "image/jpeg"  # Default
            else:
                mime_type = "image/jpeg"  # Default

    # Get approaches to use
    all_approaches = get_all_approaches()
    approaches_to_use = all_approaches

    if approaches:
        # Parse comma-separated approach names
        approach_names = [name.strip() for name in approaches.split(",")]
        approach_map = {approach.name: approach for approach in all_approaches}

        # Filter to requested approaches
        approaches_to_use = []
        invalid_approaches = []
        for name in approach_names:
            if name in approach_map:
                approaches_to_use.append(approach_map[name])
            else:
                invalid_approaches.append(name)

        if invalid_approaches:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid approach names: {', '.join(invalid_approaches)}. Available approaches: {', '.join(approach_map.keys())}",
            )

    if not approaches_to_use:
        raise HTTPException(
            status_code=503,
            detail="No recognition approaches available. Check API key configuration.",
        )

    # Run recognition (this will extract metadata and do reverse geocoding internally)
    logger.info(
        "Starting recognition: file=%s, size=%d bytes, mime=%s, approaches=%d, use_gps=%s",
        image.filename, len(image_data), mime_type, len(approaches_to_use), use_gps,
    )
    try:
        results, metadata = await recognize_image_bytes(
            image_data, mime_type, approaches_to_use, use_gps=use_gps
        )
    except Exception as e:
        logger.error("Recognition failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Recognition failed: {str(e)}"
        )

    # Build top-level metadata and google_maps_places directly from the
    # runner's enriched ImageMetadata object (no more extracting from
    # individual approach details).
    extracted_metadata: dict[str, Any] | None = None
    google_maps_places_payload: dict[str, Any] | None = None

    if use_gps and metadata:
        metadata_dict: dict[str, Any] = {}

        if metadata.gps_latitude is not None and metadata.gps_longitude is not None:
            metadata_dict["gps_latitude"] = metadata.gps_latitude
            metadata_dict["gps_longitude"] = metadata.gps_longitude

        if metadata.location_info:
            loc = metadata.location_info
            metadata_dict["location"] = {
                "formatted_address": loc.formatted_address,
                "city": loc.city,
                "county": loc.county,
                "country": loc.country,
            }

        if metadata_dict:
            extracted_metadata = metadata_dict

        # Build categorized google_maps_places payload from nearby places
        if metadata.nearby_places:
            location_name = None
            if metadata.location_info:
                loc = metadata.location_info
                parts = [
                    p for p in [
                        loc.city,
                        loc.county if loc.county != loc.city else None,
                        loc.country,
                    ]
                    if p
                ]
                location_name = ", ".join(parts) if parts else loc.formatted_address

            categorized = categorize_nearby_places(metadata.nearby_places)
            google_maps_places_payload = {
                "location_name": location_name,
                "coordinates": {
                    "latitude": metadata.gps_latitude,
                    "longitude": metadata.gps_longitude,
                },
                "search_range_meters": (
                    metadata.nearby_places_radius_meters or NEARBY_PLACES_RADIUS_METERS
                ),
                "nearby_places": categorized,
                "total_places_found": sum(len(v) for v in categorized.values()),
            }

    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    # Keys stripped from every approach's details dict.  These are either
    # already present in the top-level metadata/google_maps_places fields,
    # redundant with processing_time_ms, or too large (input_prompt).
    _DETAILS_KEYS_STRIP = frozenset({
        "gps_coordinates", "reverse_geocoding", "nearby_places",
        "geocoding_time_ms", "nearby_places_time_ms",
        "input_prompt",
        "processing_time_seconds",
    })

    def approach_to_dict(r: RecognitionResult) -> dict[str, Any]:
        out = result_to_dict(r)
        if out.get("details"):
            details = dict(out["details"])
            for key in _DETAILS_KEYS_STRIP:
                details.pop(key, None)
            out["details"] = details
        return out

    return RecognitionResponse(
        image_filename=image.filename or "unknown",
        timestamp=start_time.isoformat(),
        processing_time_seconds=processing_time,
        use_gps=use_gps,
        metadata=extracted_metadata,
        google_maps_places=google_maps_places_payload,
        approaches=[approach_to_dict(r) for r in results],
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
