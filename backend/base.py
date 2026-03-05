"""Base classes for image recognition approaches."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .metadata import ImageMetadata

# Keys that every approach's details dict should contain for consistent
# downstream consumption.  Missing keys are filled with safe defaults
# by ``normalize_details()``.
_COMMON_DETAIL_KEYS: dict[str, Any] = {
    "approach": None,
    "model": None,
    "processing_time_ms": None,
    "geocoding_time_ms": None,
    "nearby_places_time_ms": None,
    "gps_coordinates": None,
    "reverse_geocoding": None,
    "nearby_places": [],
    "description": None,
    "photographer_location": [],
    "subject_location": [],
    "entities": [],
}


def normalize_details(details: dict[str, Any] | None) -> dict[str, Any]:
    """Ensure *details* contains all common keys with safe defaults.

    Approach-specific keys (e.g. ``landmark_coordinates``,
    ``location_name``) are preserved as-is; only missing common keys
    are filled in.
    """
    if details is None:
        details = {}
    for key, default in _COMMON_DETAIL_KEYS.items():
        if key not in details:
            # Use a fresh copy for mutable defaults
            details[key] = list(default) if isinstance(default, list) else default
    return details


@dataclass
class RecognitionResult:
    """Result from an image recognition approach."""

    approach: str
    """Name of the approach that produced this result."""

    identified: str | None
    """What the approach thinks the image shows (e.g., 'Eiffel Tower, Paris')."""

    confidence: float | None
    """Confidence score 0-1, if available from the approach."""

    details: dict[str, Any] = field(default_factory=dict)
    """Approach-specific details (e.g., coordinates, sources, intermediate results)."""

    error: str | None = None
    """Error message if the approach failed."""

    @property
    def success(self) -> bool:
        """Whether the recognition succeeded."""
        return self.error is None and self.identified is not None

    def __str__(self) -> str:
        if self.error:
            return f"[{self.approach}] ERROR: {self.error}"
        if self.identified:
            conf = f" ({self.confidence:.0%})" if self.confidence else ""
            return f"[{self.approach}] {self.identified}{conf}"
        return f"[{self.approach}] No identification"


class ImageRecognitionApproach(ABC):
    """Abstract base class for image recognition approaches."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this approach."""
        pass

    @abstractmethod
    async def recognize(
        self,
        image_data: bytes,
        mime_type: str,
        metadata: ImageMetadata | None = None,
    ) -> RecognitionResult:
        """
        Recognize what is shown in an image.

        Args:
            image_data: Raw image bytes.
            mime_type: MIME type of the image (e.g., 'image/jpeg', 'image/png').
            metadata: Optional image metadata (GPS, timestamp, etc.) extracted from EXIF data.

        Returns:
            RecognitionResult with identification or error.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this approach is available (has required API keys, etc.)."""
        pass
