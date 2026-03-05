"""Main runner for parallel image recognition."""

from __future__ import annotations

import asyncio
import logging
import mimetypes
import time
from pathlib import Path

from .base import ImageRecognitionApproach, RecognitionResult
from .metadata import (
    extract_metadata,
    convert_image_to_jpeg,
    strip_exif_from_image,
    reverse_geocode,
    fetch_nearby_places,
    NEARBY_PLACES_RADIUS_METERS,
)
from .config import get_settings

logger = logging.getLogger(__name__)


def get_all_approaches() -> list[ImageRecognitionApproach]:
    """
    Get all recognition approach instances regardless of availability.

    Imports are lazy to avoid errors when optional dependencies are missing.
    """
    approaches: list[ImageRecognitionApproach] = []

    # GPT Vision Direct — fast and strong variants
    try:
        from .gpt_vision_direct.approach import GPTVisionDirectApproach
        approaches.append(GPTVisionDirectApproach(model_variant="strong"))
        approaches.append(GPTVisionDirectApproach(model_variant="fast"))
    except ImportError:
        pass

    # GPT Vision + Search — fast and strong variants
    try:
        from .gpt_vision_search.approach import GPTVisionSearchApproach
        approaches.append(GPTVisionSearchApproach(model_variant="strong"))
        approaches.append(GPTVisionSearchApproach(model_variant="fast"))
    except ImportError:
        pass

    # Gemini Vision — fast and strong variants
    try:
        from .gemini_vision.approach import GeminiVisionApproach
        approaches.append(GeminiVisionApproach(model_variant="strong"))
        approaches.append(GeminiVisionApproach(model_variant="fast"))
    except ImportError:
        pass

    # Google Cloud Vision (single, non-variant)
    try:
        from .google_cloud_vision.approach import GoogleCloudVisionApproach
        approaches.append(GoogleCloudVisionApproach())
    except ImportError:
        pass

    return approaches


def get_available_approaches() -> list[ImageRecognitionApproach]:
    """
    Get all recognition approaches that are available based on configured API keys.

    An approach is included only if .is_available() returns True.
    """
    approaches: list[ImageRecognitionApproach] = []

    # GPT Vision Direct — fast and strong variants
    try:
        from .gpt_vision_direct.approach import GPTVisionDirectApproach
        for variant in ("strong", "fast"):
            approach = GPTVisionDirectApproach(model_variant=variant)
            if approach.is_available():
                approaches.append(approach)
    except ImportError:
        pass

    # GPT Vision + Search — fast and strong variants
    try:
        from .gpt_vision_search.approach import GPTVisionSearchApproach
        for variant in ("strong", "fast"):
            approach = GPTVisionSearchApproach(model_variant=variant)
            if approach.is_available():
                approaches.append(approach)
    except ImportError:
        pass

    # Gemini Vision — fast and strong variants
    try:
        from .gemini_vision.approach import GeminiVisionApproach
        for variant in ("strong", "fast"):
            approach = GeminiVisionApproach(model_variant=variant)
            if approach.is_available():
                approaches.append(approach)
    except ImportError:
        pass

    # Google Cloud Vision (single)
    try:
        from .google_cloud_vision.approach import GoogleCloudVisionApproach
        approach = GoogleCloudVisionApproach()
        if approach.is_available():
            approaches.append(approach)
    except ImportError:
        pass

    return approaches


def detect_mime_type(image_path: str | Path) -> str:
    """Detect MIME type from file path."""
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type and mime_type.startswith("image/"):
        return mime_type
    return "image/jpeg"


def read_image(image_path: str | Path) -> bytes:
    """Read image file as bytes."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    return path.read_bytes()


async def recognize_image(
    image_path: str | Path,
    approaches: list[ImageRecognitionApproach] | None = None,
) -> list[RecognitionResult]:
    """
    Run image recognition using all available approaches in parallel.

    Args:
        image_path: Path to the image file.
        approaches: Optional list of approaches to use. If None, uses all available.

    Returns:
        List of RecognitionResult from each approach.
    """
    if approaches is None:
        approaches = get_available_approaches()

    if not approaches:
        return [
            RecognitionResult(
                approach="system",
                identified=None,
                confidence=None,
                error="No recognition approaches available. Check API key configuration.",
            )
        ]

    image_data = read_image(image_path)
    mime_type = detect_mime_type(image_path)
    metadata = extract_metadata(image_data)

    async def run_approach(approach: ImageRecognitionApproach) -> RecognitionResult:
        try:
            return await approach.recognize(image_data, mime_type, metadata)
        except Exception as e:
            logger.error("Approach %s failed: %s", approach.name, e, exc_info=True)
            return RecognitionResult(
                approach=approach.name,
                identified=None,
                confidence=None,
                error=str(e),
            )

    raw_results = await asyncio.gather(
        *[run_approach(a) for a in approaches], return_exceptions=True
    )
    # Filter: keep RecognitionResult, convert leaked exceptions to error results
    results: list[RecognitionResult] = []
    for i, r in enumerate(raw_results):
        if isinstance(r, RecognitionResult):
            results.append(r)
        elif isinstance(r, BaseException):
            approach_name = approaches[i].name if i < len(approaches) else "unknown"
            logger.error("Approach %s raised unhandled exception: %s", approach_name, r, exc_info=r)
            results.append(RecognitionResult(
                approach=approach_name,
                identified=None,
                confidence=None,
                error=str(r),
            ))
    return results


async def recognize_image_bytes(
    image_data: bytes,
    mime_type: str,
    approaches: list[ImageRecognitionApproach] | None = None,
    use_gps: bool = True,
) -> tuple[list[RecognitionResult], "ImageMetadata | None"]:
    """
    Run image recognition on raw image bytes.

    Execution flow:
    1. Extract EXIF metadata (if use_gps)
    2. Reverse geocode GPS coordinates (if available) — runs before vision approaches
    3. Fetch nearby places via Google Maps Places API (if GPS available) — enriches prompts
    4. Run all recognition approaches in parallel

    Args:
        image_data: Raw image bytes.
        mime_type: MIME type of the image.
        approaches: Optional list of approaches to use. If None, uses all available.
        use_gps: Whether to extract and use GPS from EXIF (enables location and nearby places).

    Returns:
        Tuple of (results, metadata). Results is a list of RecognitionResult from
        each approach. Metadata is the enriched ImageMetadata object (or None if
        use_gps is False or no metadata could be extracted).
    """
    from .metadata import ImageMetadata

    if approaches is None:
        approaches = get_available_approaches()

    if not approaches:
        return (
            [
                RecognitionResult(
                    approach="system",
                    identified=None,
                    confidence=None,
                    error="No recognition approaches available. Check API key configuration.",
                )
            ],
            None,
        )

    # Step 1: Extract metadata
    metadata = extract_metadata(image_data) if use_gps else None

    # Step 2: Reverse geocode GPS coordinates FIRST (if available)
    # This ensures location info is available for all vision approaches
    if metadata and metadata.gps_latitude is not None and metadata.gps_longitude is not None:
        settings = get_settings()
        if settings.google_maps_api_key:
            _t0 = time.time()
            location_info = await reverse_geocode(
                metadata.gps_latitude,
                metadata.gps_longitude,
                settings.google_maps_api_key,
            )
            metadata.location_info = location_info
            metadata.geocoding_time_ms = int((time.time() - _t0) * 1000)

            # Step 3: Fetch nearby places once (enriches vision prompts)
            _t0 = time.time()
            nearby = await fetch_nearby_places(
                metadata.gps_latitude,
                metadata.gps_longitude,
                settings.google_maps_api_key,
                radius_meters=NEARBY_PLACES_RADIUS_METERS,
            )
            metadata.nearby_places = nearby
            metadata.nearby_places_radius_meters = NEARBY_PLACES_RADIUS_METERS
            metadata.nearby_places_time_ms = int((time.time() - _t0) * 1000)

    # Convert HEIC/HEIF to JPEG for vision APIs (they don't support HEIC)
    converted_image_data, converted_mime_type = convert_image_to_jpeg(image_data, mime_type)

    # When not using GPS, strip EXIF so vision APIs cannot read location from the image
    if use_gps:
        vision_image_data = converted_image_data
        vision_mime_type = converted_mime_type
    else:
        vision_image_data, vision_mime_type = strip_exif_from_image(
            converted_image_data, converted_mime_type
        )

    # Step 4: Run all approaches in parallel
    async def run_approach(approach: ImageRecognitionApproach) -> RecognitionResult:
        start_time = time.time()
        try:
            logger.info("Starting approach: %s", approach.name)
            result = await approach.recognize(vision_image_data, vision_mime_type, metadata)
            elapsed_time = time.time() - start_time
            logger.info(
                "Approach %s completed in %.2fs (identified=%s, confidence=%s)",
                approach.name, elapsed_time, result.identified, result.confidence,
            )
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error("Approach %s failed after %.2fs: %s", approach.name, elapsed_time, e, exc_info=True)
            return RecognitionResult(
                approach=approach.name,
                identified=None,
                confidence=None,
                error=str(e),
                details={"processing_time_ms": int(elapsed_time * 1000)},
            )

    logger.info("Running %d approaches in parallel", len(approaches))
    raw_results = await asyncio.gather(
        *[run_approach(a) for a in approaches],
        return_exceptions=True,
    )

    # Filter: keep RecognitionResult, convert leaked exceptions to error results
    results: list[RecognitionResult] = []
    for i, r in enumerate(raw_results):
        if isinstance(r, RecognitionResult):
            results.append(r)
        elif isinstance(r, BaseException):
            approach_name = approaches[i].name if i < len(approaches) else "unknown"
            logger.error("Approach %s raised unhandled exception: %s", approach_name, r, exc_info=r)
            results.append(RecognitionResult(
                approach=approach_name,
                identified=None,
                confidence=None,
                error=str(r),
                details={"processing_time_ms": 0},
            ))

    return results, metadata
