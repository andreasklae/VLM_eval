"""Image metadata extraction utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Any

logger = logging.getLogger(__name__)

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_AVAILABLE = True

    # Register HEIC/HEIF support if pillow-heif is available
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    except ImportError:
        pass  # pillow-heif not installed, HEIC support unavailable
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class LocationInfo:
    """Reverse-geocoded location information from GPS coordinates."""

    formatted_address: str | None = None
    """Full formatted address (e.g., '1600 Pennsylvania Avenue NW, Washington, DC 20500, USA')."""

    city: str | None = None
    """City name (e.g., 'Washington')."""

    county: str | None = None
    """County/region name (e.g., 'District of Columbia')."""

    country: str | None = None
    """Country name (e.g., 'United States')."""

    latitude: float | None = None
    """GPS latitude used for geocoding."""

    longitude: float | None = None
    """GPS longitude used for geocoding."""


@dataclass
class NearbyPlace:
    """A place found near GPS coordinates via Google Maps Places API."""

    name: str
    type: str
    distance_meters: int
    rating: float | None = None
    vicinity: str | None = None


@dataclass
class ImageMetadata:
    """Extracted image metadata."""

    gps_latitude: float | None = None
    """GPS latitude in decimal degrees (e.g., 29.9809)."""

    gps_longitude: float | None = None
    """GPS longitude in decimal degrees (e.g., 31.1331)."""

    gps_altitude: float | None = None
    """GPS altitude in meters."""

    datetime_original: str | None = None
    """Original date/time when photo was taken (ISO format)."""

    camera_make: str | None = None
    """Camera manufacturer (e.g., 'Apple', 'Canon')."""

    camera_model: str | None = None
    """Camera model (e.g., 'iPhone 14 Pro Max')."""

    orientation: int | None = None
    """Image orientation (EXIF orientation tag)."""

    raw_exif: dict[str, Any] | None = None
    """Raw EXIF data for advanced use cases."""

    location_info: LocationInfo | None = None
    """Reverse-geocoded location information from GPS coordinates."""

    nearby_places: list[NearbyPlace] | None = None
    """Nearby places found via Google Maps Places API (None = not yet fetched)."""

    geocoding_time_ms: int | None = None
    """Time taken for reverse geocoding in milliseconds."""

    nearby_places_time_ms: int | None = None
    """Time taken for nearby places fetch in milliseconds."""

    nearby_places_radius_meters: int | None = None
    """Radius in meters used for the nearby places fetch (set by runner)."""


def extract_metadata(image_data: bytes) -> ImageMetadata:
    """
    Extract metadata from image bytes.
    
    Supports both JPEG and HEIC/HEIF formats.
    
    Args:
        image_data: Raw image bytes.
        
    Returns:
        ImageMetadata with extracted information, or empty metadata if extraction fails.
    """
    if not PIL_AVAILABLE:
        return ImageMetadata()
    
    try:
        image = Image.open(BytesIO(image_data))
        image_format = image.format
        
        # Try piexif first for both HEIC and JPEG files (more reliable for GPS data)
        if 'exif' in image.info:
            try:
                import piexif
                exif_bytes = image.info['exif']
                exif_dict = piexif.load(exif_bytes)
                metadata = _extract_metadata_from_piexif(exif_dict)
                # If piexif extraction succeeded and got GPS data, return it
                if metadata.gps_latitude is not None and metadata.gps_longitude is not None:
                    return metadata
                # Otherwise, fall through to regular extraction to get other metadata
            except ImportError:
                logger.debug("piexif not installed, falling back to Pillow EXIF extraction")
            except Exception as exc:
                logger.warning("piexif EXIF parsing failed (%s: %s), falling back to Pillow", type(exc).__name__, exc)
        
        # Try modern getexif() first (Pillow 8.0+), fall back to _getexif() for older versions
        try:
            exif = image.getexif()
        except AttributeError:
            # Fall back to deprecated _getexif() for older Pillow versions
            exif = image._getexif() if hasattr(image, '_getexif') else None
        
        if not exif:
            return ImageMetadata()
        
        metadata = ImageMetadata()
        metadata.raw_exif = {}
        
        # Extract standard EXIF tags
        # Handle both dict-like (old) and Exif object (new) formats
        exif_dict = dict(exif) if hasattr(exif, 'items') else exif
        
        for tag_id, value in exif_dict.items():
            tag = TAGS.get(tag_id, tag_id)
            metadata.raw_exif[tag] = value
            
            if tag == "DateTimeOriginal":
                metadata.datetime_original = str(value)
            elif tag == "Make":
                metadata.camera_make = str(value)
            elif tag == "Model":
                metadata.camera_model = str(value)
            elif tag == "Orientation":
                metadata.orientation = value
            elif tag == "GPSInfo":
                # Extract GPS data
                # GPSInfo can be a dict, an offset (int), or None
                if isinstance(value, dict):
                    gps_data = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_data[gps_tag] = gps_value
                    
                    # Convert GPS coordinates to decimal degrees
                    if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
                        lat = _convert_to_decimal_degrees(
                            gps_data["GPSLatitude"],
                            gps_data["GPSLatitudeRef"]
                        )
                        if lat is not None:
                            metadata.gps_latitude = lat
                    
                    if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
                        lon = _convert_to_decimal_degrees(
                            gps_data["GPSLongitude"],
                            gps_data["GPSLongitudeRef"]
                        )
                        if lon is not None:
                            metadata.gps_longitude = lon
                    
                    if "GPSAltitude" in gps_data:
                        try:
                            alt_value = gps_data["GPSAltitude"]
                            # Handle both float and rational tuple formats
                            if isinstance(alt_value, tuple) and len(alt_value) == 2:
                                metadata.gps_altitude = float(alt_value[0]) / float(alt_value[1])
                            else:
                                metadata.gps_altitude = float(alt_value)
                        except (ValueError, TypeError, ZeroDivisionError):
                            pass
                elif isinstance(value, int) and 'exif' in image.info:
                    # GPSInfo is an offset - try to extract using piexif
                    try:
                        import piexif
                        exif_bytes = image.info['exif']
                        exif_dict = piexif.load(exif_bytes)
                        if "GPS" in exif_dict and exif_dict["GPS"]:
                            gps = exif_dict["GPS"]
                            
                            if piexif.GPSIFD.GPSLatitude in gps and piexif.GPSIFD.GPSLatitudeRef in gps:
                                lat_tuple = gps[piexif.GPSIFD.GPSLatitude]
                                lat_ref = gps[piexif.GPSIFD.GPSLatitudeRef]
                                if isinstance(lat_ref, bytes):
                                    lat_ref = lat_ref.decode('utf-8', errors='ignore')
                                lat = _convert_to_decimal_degrees(lat_tuple, lat_ref)
                                if lat is not None:
                                    metadata.gps_latitude = lat
                            
                            if piexif.GPSIFD.GPSLongitude in gps and piexif.GPSIFD.GPSLongitudeRef in gps:
                                lon_tuple = gps[piexif.GPSIFD.GPSLongitude]
                                lon_ref = gps[piexif.GPSIFD.GPSLongitudeRef]
                                if isinstance(lon_ref, bytes):
                                    lon_ref = lon_ref.decode('utf-8', errors='ignore')
                                lon = _convert_to_decimal_degrees(lon_tuple, lon_ref)
                                if lon is not None:
                                    metadata.gps_longitude = lon
                    except ImportError:
                        logger.debug("piexif not installed, cannot extract GPSInfo from offset")
                    except Exception as exc:
                        logger.warning("piexif GPSInfo extraction from offset failed (%s: %s)", type(exc).__name__, exc)
        
        return metadata
        
    except Exception as exc:
        logger.warning("EXIF metadata extraction failed (%s: %s), returning empty metadata", type(exc).__name__, exc)
        return ImageMetadata()


def _extract_metadata_from_piexif(exif_dict: dict) -> ImageMetadata:
    """Extract metadata from piexif EXIF dictionary (used for HEIC files)."""
    try:
        import piexif
    except ImportError:
        return ImageMetadata()  # piexif not available
    
    metadata = ImageMetadata()
    
    # Extract from "0th" (main) IFD
    if "0th" in exif_dict:
        main = exif_dict["0th"]
        if piexif.ImageIFD.Make in main:
            metadata.camera_make = main[piexif.ImageIFD.Make].decode('utf-8', errors='ignore')
        if piexif.ImageIFD.Model in main:
            metadata.camera_model = main[piexif.ImageIFD.Model].decode('utf-8', errors='ignore')
        if piexif.ImageIFD.Orientation in main:
            metadata.orientation = main[piexif.ImageIFD.Orientation]
        if piexif.ImageIFD.DateTime in main:
            metadata.datetime_original = main[piexif.ImageIFD.DateTime].decode('utf-8', errors='ignore')
    
    # Extract from "Exif" IFD
    if "Exif" in exif_dict:
        exif = exif_dict["Exif"]
        if piexif.ExifIFD.DateTimeOriginal in exif:
            metadata.datetime_original = exif[piexif.ExifIFD.DateTimeOriginal].decode('utf-8', errors='ignore')
    
    # Extract GPS data
    if "GPS" in exif_dict and exif_dict["GPS"]:
        gps = exif_dict["GPS"]
        
        if piexif.GPSIFD.GPSLatitude in gps and piexif.GPSIFD.GPSLatitudeRef in gps:
            lat_tuple = gps[piexif.GPSIFD.GPSLatitude]
            lat_ref = gps[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8', errors='ignore')
            lat = _convert_to_decimal_degrees(lat_tuple, lat_ref)
            if lat is not None:
                metadata.gps_latitude = lat
        
        if piexif.GPSIFD.GPSLongitude in gps and piexif.GPSIFD.GPSLongitudeRef in gps:
            lon_tuple = gps[piexif.GPSIFD.GPSLongitude]
            lon_ref = gps[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8', errors='ignore')
            lon = _convert_to_decimal_degrees(lon_tuple, lon_ref)
            if lon is not None:
                metadata.gps_longitude = lon
        
        if piexif.GPSIFD.GPSAltitude in gps:
            try:
                # GPSAltitude is stored as a rational (numerator, denominator)
                alt_tuple = gps[piexif.GPSIFD.GPSAltitude]
                if isinstance(alt_tuple, tuple) and len(alt_tuple) == 2:
                    metadata.gps_altitude = float(alt_tuple[0]) / float(alt_tuple[1])
                else:
                    metadata.gps_altitude = float(alt_tuple)
            except (ValueError, TypeError, ZeroDivisionError):
                pass
    
    return metadata


def strip_exif_from_image(image_data: bytes, mime_type: str) -> tuple[bytes, str]:
    """
    Return image bytes with EXIF removed (no GPS or other metadata in the file).

    Used when use_gps is False so vision APIs cannot read location from the image.
    Re-encodes as JPEG without EXIF; non-JPEG inputs are converted to JPEG.

    Returns:
        Tuple of (image_bytes, "image/jpeg"). Original if PIL unavailable.
    """
    if not PIL_AVAILABLE:
        return image_data, mime_type
    try:
        image = Image.open(BytesIO(image_data))
        if image.mode in ("RGBA", "LA", "P"):
            rgb = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            rgb.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
            image = rgb
        elif image.mode != "RGB":
            image = image.convert("RGB")
        out = BytesIO()
        image.save(out, format="JPEG", quality=95)  # no exif= parameter → no EXIF
        return out.getvalue(), "image/jpeg"
    except Exception as exc:
        logger.warning("EXIF stripping failed (%s: %s), returning original image", type(exc).__name__, exc)
        return image_data, mime_type


def convert_image_to_jpeg(image_data: bytes, mime_type: str) -> tuple[bytes, str]:
    """
    Convert image to JPEG format if needed.
    
    Vision APIs typically don't support HEIC/HEIF, so we convert to JPEG.
    
    Args:
        image_data: Raw image bytes.
        mime_type: Original MIME type.
        
    Returns:
        Tuple of (converted_image_bytes, "image/jpeg")
    """
    if not PIL_AVAILABLE:
        return image_data, mime_type
    
    # Check if conversion is needed
    heic_types = {"image/heic", "image/heif", "image/heics", "image/heifs"}
    if mime_type.lower() not in heic_types:
        return image_data, mime_type
    
    try:
        # Open and convert to JPEG
        image = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if needed (JPEG doesn't support transparency)
        if image.mode in ("RGBA", "LA", "P"):
            # Create white background
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            rgb_image.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
            image = rgb_image
        elif image.mode != "RGB":
            image = image.convert("RGB")
        
        # Save as JPEG to bytes
        output = BytesIO()
        image.save(output, format="JPEG", quality=95)
        return output.getvalue(), "image/jpeg"
        
    except Exception as exc:
        logger.warning("HEIC-to-JPEG conversion failed (%s: %s), returning original image", type(exc).__name__, exc)
        return image_data, mime_type


async def reverse_geocode(latitude: float, longitude: float, google_maps_api_key: str) -> LocationInfo | None:
    """
    Reverse geocode GPS coordinates to get location information.

    Uses Google Maps Geocoding API to convert coordinates to human-readable location.

    Args:
        latitude: GPS latitude in decimal degrees.
        longitude: GPS longitude in decimal degrees.
        google_maps_api_key: Google Maps API key.

    Returns:
        LocationInfo with address, city, county, country, or None if geocoding fails.
    """
    if not google_maps_api_key:
        return None

    try:
        import httpx
    except ImportError:
        return None  # httpx not available

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{latitude},{longitude}",
        "key": google_maps_api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, dict) or data.get("status") != "OK" or not data.get("results"):
            return None

        results_list = data["results"]
        if not isinstance(results_list, list) or len(results_list) == 0:
            return None

        # Get the most specific result (first one is usually most specific)
        result = results_list[0]
        if not isinstance(result, dict):
            return None

        # Extract formatted address
        formatted_address = result.get("formatted_address")

        # Extract structured components
        city = None
        county = None
        country = None

        components = result.get("address_components", [])
        for comp in components:
            types = comp.get("types", [])
            long_name = comp.get("long_name")

            if "locality" in types and not city:
                city = long_name
            elif "administrative_area_level_2" in types and not county:
                county = long_name
            elif "administrative_area_level_1" in types and not county:
                # Use level 1 if level 2 not found (some countries don't have level 2)
                county = long_name
            elif "country" in types:
                country = long_name

        return LocationInfo(
            formatted_address=formatted_address,
            city=city,
            county=county,
            country=country,
            latitude=latitude,
            longitude=longitude,
        )

    except Exception as exc:
        logger.warning("Reverse geocoding failed for (%.6f, %.6f): %s: %s", latitude, longitude, type(exc).__name__, exc)
        return None


# Single radius used for nearby places everywhere (runner enrichment).
NEARBY_PLACES_RADIUS_METERS = 2000

# Place types we query for prompt enrichment. Only types relevant to
# tourism/landmarks/culture — excludes institutional types (library,
# courthouse, university) that add noise to recognition prompts.
ENRICHMENT_PLACE_TYPES = [
    "tourist_attraction", "museum", "art_gallery",
    "church", "mosque", "synagogue", "hindu_temple",
    "park", "natural_feature",
    "stadium", "city_hall",
    "amusement_park", "zoo", "aquarium",
    "cemetery",
]


def _type_to_category(place_type: str) -> str:
    """Map a Google Places API type to a human-readable category name."""
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
        "city_hall": "city_halls",
        "amusement_park": "amusement_parks",
        "zoo": "zoos",
        "aquarium": "aquariums",
        "cemetery": "cemeteries",
    }
    return type_map.get(place_type, "other")


def categorize_nearby_places(places: list[NearbyPlace]) -> dict[str, list[dict]]:
    """Group nearby places by category.

    Returns a dict mapping category name to a list of place dicts,
    e.g. ``{"landmarks": [{"name": ..., "types": [...], ...}], ...}``.
    """
    categorized: dict[str, list[dict]] = {}
    for place in places:
        category = _type_to_category(place.type)
        if category not in categorized:
            categorized[category] = []
        categorized[category].append({
            "name": place.name,
            "types": [place.type],
            "rating": place.rating,
            "vicinity": place.vicinity,
            "distance_meters": place.distance_meters,
        })
    return categorized


async def fetch_nearby_places(
    latitude: float,
    longitude: float,
    google_maps_api_key: str,
    radius_meters: int = NEARBY_PLACES_RADIUS_METERS,
) -> list[NearbyPlace]:
    """
    Fetch nearby places of interest using Google Maps Places API.

    Searches place types from ENRICHMENT_PLACE_TYPES (landmarks, culture, nature;
    excludes e.g. lodging and transit). Results are sorted by distance.

    Args:
        latitude: GPS latitude in decimal degrees.
        longitude: GPS longitude in decimal degrees.
        google_maps_api_key: Google Maps API key.
        radius_meters: Search radius in meters (default NEARBY_PLACES_RADIUS_METERS).

    Returns:
        List of NearbyPlace objects, sorted by distance.
    """
    if not google_maps_api_key:
        return []

    try:
        import httpx
        import math
    except ImportError:
        return []

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    all_places: dict[str, NearbyPlace] = {}  # keyed by place_id to deduplicate

    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
        """Calculate distance in meters between two GPS coordinates."""
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return int(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    async def _search_type(client: "httpx.AsyncClient", place_type: str) -> None:
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius_meters,
            "type": place_type,
            "key": google_maps_api_key,
        }
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") not in ("OK", "ZERO_RESULTS"):
                return
            for item in data.get("results", []):
                place_id = item.get("place_id", "")
                if not place_id or place_id in all_places:
                    continue
                loc = item.get("geometry", {}).get("location", {})
                place_lat = loc.get("lat", latitude)
                place_lng = loc.get("lng", longitude)
                distance = _haversine_distance(latitude, longitude, place_lat, place_lng)
                types = item.get("types", [])
                # Use the most specific non-generic type
                primary_type = next(
                    (t for t in types if t not in ("point_of_interest", "establishment")),
                    types[0] if types else place_type,
                )
                all_places[place_id] = NearbyPlace(
                    name=item.get("name", ""),
                    type=primary_type,
                    distance_meters=distance,
                    rating=item.get("rating"),
                    vicinity=item.get("vicinity"),
                )
        except Exception as exc:
            logger.debug("Nearby places search for type '%s' failed: %s: %s", place_type, type(exc).__name__, exc)

    try:
        import asyncio
        async with httpx.AsyncClient(timeout=15.0) as client:
            await asyncio.gather(*[_search_type(client, pt) for pt in ENRICHMENT_PLACE_TYPES])
    except Exception as exc:
        logger.warning("Nearby places fetch failed for (%.6f, %.6f): %s: %s", latitude, longitude, type(exc).__name__, exc)
        return []

    # Sort by distance, return closest places first
    return sorted(all_places.values(), key=lambda p: p.distance_meters)


def _convert_to_decimal_degrees(coord_tuple: tuple, ref: str) -> float | None:
    """
    Convert GPS coordinate tuple to decimal degrees.

    Handles both formats:
    - Simple tuples: (degrees, minutes, seconds)
    - Rational tuples (piexif): ((num, den), (num, den), (num, den))

    Args:
        coord_tuple: Tuple of (degrees, minutes, seconds) or rational tuples
        ref: Reference direction ('N', 'S', 'E', 'W') - can be bytes or str

    Returns:
        Decimal degrees, or None if conversion fails.
    """
    try:
        # Handle bytes reference
        if isinstance(ref, bytes):
            ref = ref.decode('utf-8', errors='ignore')

        if len(coord_tuple) >= 3:
            # Check if first element is a tuple (rational number format from piexif)
            if isinstance(coord_tuple[0], tuple) and len(coord_tuple[0]) == 2:
                # Rational format: ((num, den), (num, den), (num, den))
                degrees_num, degrees_den = coord_tuple[0]
                minutes_num, minutes_den = coord_tuple[1]
                seconds_num, seconds_den = coord_tuple[2]

                degrees = float(degrees_num) / float(degrees_den) if degrees_den != 0 else float(degrees_num)
                minutes = float(minutes_num) / float(minutes_den) if minutes_den != 0 else float(minutes_num)
                seconds = float(seconds_num) / float(seconds_den) if seconds_den != 0 else float(seconds_num)
            else:
                # Simple format: (degrees, minutes, seconds)
                degrees = float(coord_tuple[0])
                minutes = float(coord_tuple[1])
                seconds = float(coord_tuple[2])

            decimal = degrees + minutes / 60.0 + seconds / 3600.0

            # Apply sign based on reference
            if ref in ("S", "W"):
                decimal = -decimal

            return decimal
    except (ValueError, TypeError, IndexError, ZeroDivisionError):
        pass

    return None
