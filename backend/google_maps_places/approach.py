"""Google Maps Places approach - uses GPS coordinates to find location and nearby categorized places.

When metadata.nearby_places is set by the runner (single fetch), this approach builds its
response from that data only. No duplicate Places API calls; same radius as enrichment.
"""

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

from ..base import ImageRecognitionApproach, RecognitionResult
from ..config import get_settings
from ..metadata import ImageMetadata, NEARBY_PLACES_RADIUS_METERS


class GoogleMapsPlacesApproach(ImageRecognitionApproach):
    """
    Uses Google Maps Places API to identify photo location and find nearby categorized places.
    
    Only runs when GPS coordinates are available in image metadata.
    """

    def __init__(self):
        self.settings = get_settings()

    @property
    def name(self) -> str:
        return "Google Maps Places"

    def is_available(self) -> bool:
        """Check if Google Maps Places API is available."""
        return bool(self.settings.google_maps_api_key)

    def set_search_range(self, range_meters: int | None) -> None:
        """
        Deprecated: nearby places are now fetched once in the runner and reused.
        Kept for backward compatibility; no longer used.
        """
        pass

    async def _reverse_geocode(
        self, latitude: float, longitude: float
    ) -> str | None:
        """
        Get location name from coordinates using reverse geocoding.
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            
        Returns:
            Location name (e.g., "Paris, France") or None if not found
        """
        if not self.is_available():
            return None

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": self.settings.google_maps_api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                # Get the most specific result (first one is usually most specific)
                result = data["results"][0]
                # Try to get a readable location name
                # Look for formatted_address or extract from address_components
                location_name = result.get("formatted_address")
                if location_name:
                    return location_name

                # Fallback: construct from address components
                components = result.get("address_components", [])
                parts = []
                for comp in components:
                    types = comp.get("types", [])
                    if "locality" in types or "administrative_area_level_1" in types:
                        parts.append(comp.get("long_name"))
                    elif "country" in types:
                        parts.append(comp.get("long_name"))
                if parts:
                    return ", ".join(parts)

        except Exception as exc:
            logger.warning("Reverse geocode failed for (%.6f, %.6f): %s: %s", latitude, longitude, type(exc).__name__, exc)

        return None

    async def _search_nearby_places(
        self,
        latitude: float,
        longitude: float,
        radius: int,
        place_type: str,
    ) -> list[dict[str, Any]]:
        """
        Search for nearby places of a specific type.
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            radius: Search radius in meters
            place_type: Place type to search for
            
        Returns:
            List of place dictionaries
        """
        if not self.is_available():
            return []

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "type": place_type,
            "key": self.settings.google_maps_api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            if data.get("status") == "OK":
                results = data.get("results", [])
                places = []
                for result in results[:5]:  # Limit to top 5 per type
                    place = {
                        "name": result.get("name"),
                        "types": result.get("types", []),
                        "rating": result.get("rating"),
                        "user_ratings_total": result.get("user_ratings_total"),
                        "vicinity": result.get("vicinity"),
                        "place_id": result.get("place_id"),
                    }
                    # Add location if available
                    geometry = result.get("geometry", {})
                    location = geometry.get("location", {})
                    if location:
                        place["location"] = {
                            "lat": location.get("lat"),
                            "lng": location.get("lng"),
                        }
                    places.append(place)
                return places

        except Exception as exc:
            logger.warning("Nearby places search failed for type '%s': %s: %s", place_type, type(exc).__name__, exc)

        return []

    async def recognize(
        self,
        image_data: bytes,
        mime_type: str,
        metadata: ImageMetadata | None = None,
    ) -> RecognitionResult:
        """
        Identify location and find nearby categorized places using GPS coordinates.
        
        Only runs if GPS coordinates are available in metadata.
        """
        if not self.is_available():
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error="Google Maps Places API not available. Check GOOGLE_MAPS_API_KEY.",
            )

        # Check if GPS coordinates are available
        if not metadata or metadata.gps_latitude is None or metadata.gps_longitude is None:
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error="GPS coordinates not available in image metadata.",
            )

        start_time = time.time()
        try:
            latitude = metadata.gps_latitude
            longitude = metadata.gps_longitude

            # Use cached reverse geocoded location if available, otherwise do it now
            if metadata.location_info:
                loc = metadata.location_info
                location_parts = []
                if loc.city:
                    location_parts.append(loc.city)
                if loc.county and loc.county != loc.city:
                    location_parts.append(loc.county)
                if loc.country:
                    location_parts.append(loc.country)
                location_name = ", ".join(location_parts) if location_parts else loc.formatted_address
            else:
                location_name = await self._reverse_geocode(latitude, longitude)

            # Build from runner's single nearby-places fetch (no duplicate API calls)
            search_range = getattr(
                metadata, "nearby_places_radius_meters", None
            ) or NEARBY_PLACES_RADIUS_METERS
            categorized_places: dict[str, list[dict[str, Any]]] = {}
            if metadata.nearby_places:
                for place in metadata.nearby_places:
                    category = self._type_to_category(place.type)
                    if category not in categorized_places:
                        categorized_places[category] = []
                    categorized_places[category].append({
                        "name": place.name,
                        "types": [place.type],
                        "rating": place.rating,
                        "vicinity": place.vicinity,
                        "distance_meters": place.distance_meters,
                    })

            # Build identification string
            if location_name:
                identified = location_name
            else:
                identified = f"Location at {latitude:.6f}, {longitude:.6f}"

            # Build details (same radius as enrichment)
            details: dict[str, Any] = {
                "location_name": location_name,
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "search_range_meters": search_range,
                "nearby_places": categorized_places,
                "total_places_found": sum(len(places) for places in categorized_places.values()),
                "processing_time_ms": int((time.time() - start_time) * 1000),
            }

            # Add metadata if available
            if metadata.datetime_original:
                details["photo_timestamp"] = metadata.datetime_original
            if metadata.camera_make or metadata.camera_model:
                details["camera"] = {
                    "make": metadata.camera_make,
                    "model": metadata.camera_model,
                }

            return RecognitionResult(
                approach=self.name,
                identified=identified,
                confidence=1.0 if location_name else 0.8,  # High confidence if we got location name
                details=details,
            )

        except Exception as e:
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error=str(e),
            )

    @staticmethod
    def _type_to_category(place_type: str) -> str:
        """Map Google Places API type to category name (covers ENRICHMENT_PLACE_TYPES)."""
        type_map = {
            "tourist_attraction": "landmarks",
            "museum": "museums",
            "art_gallery": "art_galleries",
            "church": "religious_sites",
            "mosque": "religious_sites",
            "synagogue": "religious_sites",
            "hindu_temple": "religious_sites",
            "park": "parks",
            "natural_feature": "natural_features",
            "stadium": "stadiums",
            "library": "libraries",
            "city_hall": "city_halls",
            "courthouse": "courthouses",
            "university": "universities",
            "amusement_park": "amusement_parks",
            "zoo": "zoos",
            "aquarium": "aquariums",
            "cemetery": "cemeteries",
            "restaurant": "restaurants",
            "viewpoint": "viewpoints",
        }
        return type_map.get(place_type, "other")
