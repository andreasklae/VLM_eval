"""Test script for reverse geocoding functionality."""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

from metadata import reverse_geocode


async def test_reverse_geocode():
    """Test reverse geocoding with known coordinates."""
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not google_maps_api_key:
        print("ERROR: GOOGLE_MAPS_API_KEY not found in environment")
        return

    # Test coordinates for Oslo, Norway (Akershus Fortress)
    test_locations = [
        ("Oslo, Norway", 59.9075, 10.7365),
        ("Paris, France", 48.8584, 2.2945),  # Eiffel Tower
        ("New York, USA", 40.6892, -74.0445),  # Statue of Liberty
    ]

    for name, lat, lon in test_locations:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"Coordinates: {lat}, {lon}")
        print(f"{'='*60}")

        location_info = await reverse_geocode(lat, lon, google_maps_api_key)

        if location_info:
            print(f"✓ Reverse geocoding successful!")
            print(f"  Formatted address: {location_info.formatted_address}")
            print(f"  City: {location_info.city}")
            print(f"  County: {location_info.county}")
            print(f"  Country: {location_info.country}")
        else:
            print(f"✗ Reverse geocoding failed")


if __name__ == "__main__":
    asyncio.run(test_reverse_geocode())
