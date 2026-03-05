#!/usr/bin/env python3
"""
Write GPS coordinates into image EXIF metadata.

Usage:
  python write_gps_metadata.py

Expects a COORDS mapping in this file (or pass path to a JSON file).
JSON format: {"1.jpg": [lat, lon], "2.jpg": [59.91, 10.75], ...}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Optional: allow running from project root
SCRIPT_DIR = Path(__file__).resolve().parent
TEST_IMAGES_DIR = SCRIPT_DIR / "test_images"

# --- Add your coordinates here (filename -> [latitude, longitude]) ---
# Example: COORDS = {"1.jpg": [59.9127, 10.7461], "2.jpg": [60.3920, 5.3235]}
COORDS: dict[str, list[float]] = {
    "1.jpg": [67.518905, 14.758099],
    "2.jpg": [45.464428, 9.190310],
    "3.jpg": [61.124585, 10.485589],
    "4.jpg": [47.801807, 13.042212],
    "5.jpg": [59.910848, 10.727052],
    "6.jpg": [37.776037, -122.433494],
    "7.jpg": [59.916171, 10.716302],
    "8.jpg": [50.062155, 19.938448],
    "9.jpg": [32.712832, -117.175177],
    "10.jpg": [59.930107, 10.757268],
    "11.jpg": [38.716552, -9.131625],
    "12.jpg": [61.344480, 10.076528],
    "13.jpg": [59.913288, 10.740633],
    "14.jpg": [58.994925, 10.039144],
    "15.jpg": [52.503895, 13.442831],
    "16.jpg": [29.975354, 31.139170],
}


def decimal_to_dms_rational(decimal_deg: float) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    """Convert decimal degrees to EXIF rational (deg, min, sec) as ((n,d), (n,d), (n,d)). Uses absolute value; sign is encoded in Ref (N/S, E/W)."""
    decimal_deg = abs(decimal_deg)
    degrees = int(decimal_deg)
    remainder = (decimal_deg - degrees) * 60
    minutes = int(remainder)
    seconds = (remainder - minutes) * 60
    # EXIF rational: use 1 for deg/min, and 1000 for seconds for precision
    return ((degrees, 1), (minutes, 1), (int(round(seconds * 1000)), 1000))


def set_gps_in_exif(exif_dict: dict, latitude: float, longitude: float) -> None:
    """Set GPS latitude/longitude in a piexif exif_dict (in-place)."""
    import piexif

    lat_dms = decimal_to_dms_rational(latitude)
    lon_dms = decimal_to_dms_rational(longitude)
    ref_lat = b"N" if latitude >= 0 else b"S"
    ref_lon = b"E" if longitude >= 0 else b"W"

    if "GPS" not in exif_dict:
        exif_dict["GPS"] = {}
    gps = exif_dict["GPS"]
    gps[piexif.GPSIFD.GPSLatitude] = lat_dms
    gps[piexif.GPSIFD.GPSLatitudeRef] = ref_lat
    gps[piexif.GPSIFD.GPSLongitude] = lon_dms
    gps[piexif.GPSIFD.GPSLongitudeRef] = ref_lon


def write_gps_to_image(image_path: Path, latitude: float, longitude: float) -> None:
    """Read image, inject GPS into EXIF, write back (overwrites file)."""
    import piexif
    from PIL import Image

    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(path)

    data = path.read_bytes()
    try:
        exif_dict = piexif.load(data)
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    set_gps_in_exif(exif_dict, latitude, longitude)
    exif_bytes = piexif.dump(exif_dict)

    image = Image.open(path)
    # Preserve mode (e.g. RGB) and save with new EXIF
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(path, "JPEG", quality=95, exif=exif_bytes)


def main() -> None:
    coords = COORDS.copy()

    # Optional: load from JSON file
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
        if json_path.is_file():
            coords = json.loads(json_path.read_text())
        else:
            print(f"File not found: {json_path}", file=sys.stderr)
            sys.exit(1)

    if not coords:
        print("No coordinates defined. Edit COORDS in this script or pass a JSON file.", file=sys.stderr)
        sys.exit(1)

    for filename, lat_lon in coords.items():
        path = TEST_IMAGES_DIR / filename
        if not path.exists():
            print(f"Skip (not found): {filename}")
            continue
        lat, lon = lat_lon[0], lat_lon[1]
        try:
            write_gps_to_image(path, lat, lon)
            print(f"OK: {filename} -> ({lat}, {lon})")
        except Exception as e:
            print(f"Error {filename}: {e}", file=sys.stderr)

    print("Done.")


if __name__ == "__main__":
    main()
