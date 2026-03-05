"""Google Cloud Vision approach - landmark detection, web detection, and OCR text detection."""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

from ..base import ImageRecognitionApproach, RecognitionResult
from ..config import get_settings
from ..metadata import ImageMetadata
from ..schema import Entity, EntityType


# Minimum score threshold for web entity inclusion (lower = more entities, noisier)
WEB_ENTITY_MIN_SCORE = 0.5

# Minimum character length for OCR text blocks to be included as entities
OCR_MIN_LENGTH = 4

# Generic stopwords to exclude from OCR results
OCR_STOPWORDS = {
    "the", "and", "for", "www", "com", "org", "net", "http", "https",
    "open", "closed", "exit", "enter", "stop", "yes", "no", "ok",
}

# Art-related keywords for web entity type detection
_ART_KEYWORDS = {
    "painting", "artwork", "art", "masterpiece", "canvas", "portrait",
    "landscape", "still life", "sculpture", "fresco", "mural", "mosaic",
    "lithograph", "etching", "watercolor", "drawing", "sketch",
}

# Museum/gallery keywords
_MUSEUM_KEYWORDS = {
    "museum", "gallery", "collection", "exhibition", "louvre", "metropolitan",
    "moma", "tate", "uffizi", "prado", "hermitage", "rijksmuseum",
}


def _ocr_text_is_useful(text: str) -> bool:
    """
    Decide whether an OCR-detected text block is worth including as a signage entity.

    Filters out:
    - Strings shorter than OCR_MIN_LENGTH characters
    - Purely numeric strings
    - Strings matching known generic stopwords (case-insensitive)
    """
    stripped = text.strip()
    if len(stripped) < OCR_MIN_LENGTH:
        return False
    if stripped.isdigit():
        return False
    if stripped.lower() in OCR_STOPWORDS:
        return False
    return True


# Generic/abstract concepts that should NOT be classified as landmarks.
# These appear frequently as Cloud Vision web entities but refer to broad
# topics rather than specific identifiable places.
_GENERIC_CONCEPTS = {
    "tourism", "travel", "vacation", "holiday", "trip",
    "photograph", "photography", "image", "picture", "photo",
    "history", "culture", "heritage", "architecture",
    "nature", "landscape", "scenery", "view",
    "city", "town", "village", "urban", "rural",
    "europe", "asia", "africa", "americas",
    "wikipedia", "wikimedia",
}


def _web_entity_type(description: str) -> EntityType:
    """Infer EntityType for a web entity based on its description text."""
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in _ART_KEYWORDS):
        return EntityType.ARTWORK
    if any(kw in desc_lower for kw in _MUSEUM_KEYWORDS):
        return EntityType.CULTURAL_SITE
    if desc_lower in _GENERIC_CONCEPTS:
        return EntityType.OTHER
    return EntityType.LANDMARK


class GoogleCloudVisionApproach(ImageRecognitionApproach):
    """
    Identifies visual content using Google Cloud Vision API.

    Detection types used:
    - landmark_detection: Named geographic landmarks
    - web_detection: Web entities with score >= WEB_ENTITY_MIN_SCORE (0.5)
    - text_detection (OCR): Readable text on signs, plaques, inscriptions

    label_detection and object_localization are NOT called (removed per redesign).
    If no landmark or strong web entities are found, returns identified=None.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    @property
    def name(self) -> str:
        return "Google Cloud Vision"

    def is_available(self) -> bool:
        """Check if Google Cloud Vision is available."""
        if not self.settings.google_vision_available:
            return False
        try:
            from google.cloud import vision  # noqa: F401
            return True
        except ImportError:
            return False

    def _get_client(self):
        """Get or create Vision API client."""
        if self._client is None:
            from google.cloud import vision
            self._client = vision.ImageAnnotatorClient()
        return self._client

    def _build_full_record(
        self,
        metadata: ImageMetadata | None,
        entities: list[Entity],
        processing_time_ms: int,
        landmark_name: str | None,
        landmark_score: float | None,
        landmark_coordinates: dict | None,
        web_entities_raw: list[dict],
        ocr_texts: list[str],
    ) -> dict[str, Any]:
        """
        Assemble the standardized full_record for Cloud Vision results.

        AI-generated fields (description, photographer_location, subject_location)
        are set to None since Cloud Vision does not produce them.
        """
        record: dict[str, Any] = {
            "approach": self.name,
            "model": "google-cloud-vision-api",
            "processing_time_ms": processing_time_ms,
            "geocoding_time_ms": None,
            "nearby_places_time_ms": None,
            "gps_coordinates": None,
            "reverse_geocoding": None,
            "nearby_places": [],
            # AI-only fields — not available from Cloud Vision
            "input_prompt": None,
            "description": None,
            "photographer_location": [],
            "subject_location": [],
            # Populated from detection results
            "entities": [
                {
                    "name": e.name,
                    "type": e.type.value,
                    "confidence": e.confidence,
                    "notes": e.notes,
                }
                for e in entities
            ],
            # Cloud Vision-specific details
            "landmark_name": landmark_name,
            "landmark_score": landmark_score,
            "landmark_coordinates": landmark_coordinates,
            "web_entities_raw": web_entities_raw,
            "ocr_texts": ocr_texts,
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

    async def recognize(
        self,
        image_data: bytes,
        mime_type: str,
        metadata: ImageMetadata | None = None,
    ) -> RecognitionResult:
        """Identify visual content using landmark detection, web detection, and OCR."""
        if not self.is_available():
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error=(
                    "Google Cloud Vision not available. "
                    "Check GOOGLE_APPLICATION_CREDENTIALS and install google-cloud-vision."
                ),
            )

        start_time = time.time()

        try:
            from google.cloud import vision

            client = self._get_client()
            image = vision.Image(content=image_data)
            logger.info("[%s] Calling Cloud Vision API (image_size=%d bytes)", self.name, len(image_data))

            # Run landmark detection, web detection, and text/OCR detection
            # (label_detection and object_localization are intentionally NOT called)
            landmark_response = client.landmark_detection(image=image)
            web_response = client.web_detection(image=image)
            text_response = client.text_detection(image=image)

            # Check for API error on landmark response
            if landmark_response.error.message:
                return RecognitionResult(
                    approach=self.name,
                    identified=None,
                    confidence=None,
                    error=f"API error: {landmark_response.error.message}",
                )

            landmarks = landmark_response.landmark_annotations
            web = web_response.web_detection if not web_response.error.message else None
            text_annotations = (
                text_response.text_annotations if not text_response.error.message else []
            )

            # --- Build entity list from all sources ---
            entities: list[Entity] = []
            primary_identified: str | None = None
            primary_confidence: float | None = None

            # (1) Landmark detection — highest priority, most precise
            landmark_name: str | None = None
            landmark_score: float | None = None
            landmark_coordinates: dict | None = None

            if landmarks:
                top = landmarks[0]
                landmark_name = top.description
                landmark_score = float(top.score) if top.score else None

                if top.locations:
                    loc = top.locations[0].lat_lng
                    landmark_coordinates = {
                        "latitude": loc.latitude,
                        "longitude": loc.longitude,
                    }

                entities.append(Entity(
                    name=landmark_name,
                    type=EntityType.LANDMARK,
                    confidence=landmark_score or 0.0,
                    notes=None,
                ))

                # Additional landmarks at lower confidence
                for lm in landmarks[1:5]:
                    if lm.score and lm.score >= 0.3:
                        entities.append(Entity(
                            name=lm.description,
                            type=EntityType.LANDMARK,
                            confidence=float(lm.score),
                            notes=None,
                        ))

                primary_identified = landmark_name
                primary_confidence = landmark_score

            # (2) Web entities (score >= threshold) — deduplication by name
            web_entities_raw: list[dict] = []
            seen_web_names: set[str] = set()

            if web and web.web_entities:
                for entity in web.web_entities:
                    if not entity.score or entity.score < WEB_ENTITY_MIN_SCORE:
                        continue
                    name = entity.description
                    if not name or name.lower() in seen_web_names:
                        continue
                    seen_web_names.add(name.lower())
                    web_entities_raw.append({"name": name, "score": float(entity.score)})

                    entity_type = _web_entity_type(name)
                    entities.append(Entity(
                        name=name,
                        type=entity_type,
                        confidence=min(float(entity.score), 1.0),
                        notes=None,
                    ))

                    # If no landmark found, best web entity becomes primary
                    if primary_identified is None and entity.score >= WEB_ENTITY_MIN_SCORE:
                        primary_identified = name
                        primary_confidence = float(entity.score)

            # (3) OCR / text detection
            # text_annotations[0] (if present) is the full-image text block — skip it
            # text_annotations[1:] are individual word/block annotations
            ocr_texts: list[str] = []

            for annotation in text_annotations[1:]:
                text = (annotation.description or "").strip()
                if _ocr_text_is_useful(text):
                    if text not in ocr_texts:
                        ocr_texts.append(text)
                        entities.append(Entity(
                            name=text,
                            type=EntityType.SIGNAGE,
                            confidence=0.9,  # OCR text is deterministic; confidence is high
                            notes="Detected via OCR",
                        ))

            processing_ms = int((time.time() - start_time) * 1000)

            # If nothing useful was found, return no identification
            if primary_identified is None:
                return RecognitionResult(
                    approach=self.name,
                    identified=None,
                    confidence=None,
                    details=self._build_full_record(
                        metadata=metadata,
                        entities=entities,
                        processing_time_ms=processing_ms,
                        landmark_name=None,
                        landmark_score=None,
                        landmark_coordinates=None,
                        web_entities_raw=web_entities_raw,
                        ocr_texts=ocr_texts,
                    ),
                )

            full_record = self._build_full_record(
                metadata=metadata,
                entities=entities,
                processing_time_ms=processing_ms,
                landmark_name=landmark_name,
                landmark_score=landmark_score,
                landmark_coordinates=landmark_coordinates,
                web_entities_raw=web_entities_raw,
                ocr_texts=ocr_texts,
            )

            return RecognitionResult(
                approach=self.name,
                identified=primary_identified,
                confidence=primary_confidence,
                details=full_record,
            )

        except ImportError:
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error="google-cloud-vision package not installed. Run: pip install google-cloud-vision",
            )
        except Exception as e:
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error=str(e),
                details={"processing_time_ms": int((time.time() - start_time) * 1000)},
            )
