#!/usr/bin/env python3
"""List all images in test_images/ that do not have GPS in metadata."""

import sys
from pathlib import Path

# Allow importing from backend/image_recognition
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.image_recognition.metadata import extract_metadata

TEST_IMAGES_DIR = Path(__file__).resolve().parent / "test_images"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".heic", ".heif"}


def main() -> None:
    image_files = sorted(
        f for f in TEST_IMAGES_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    )
    no_gps: list[str] = []
    with_gps: list[str] = []
    errors: list[tuple[str, str]] = []

    for path in image_files:
        name = path.name
        try:
            data = path.read_bytes()
            meta = extract_metadata(data)
            if meta.gps_latitude is not None and meta.gps_longitude is not None:
                with_gps.append(name)
            else:
                no_gps.append(name)
        except Exception as e:
            errors.append((name, str(e)))

    print("Images WITHOUT GPS in metadata:")
    print("-" * 40)
    for name in no_gps:
        print(name)
    print()
    print(f"Total without GPS: {len(no_gps)}")
    print(f"Total with GPS: {len(with_gps)}")
    print(f"Total images checked: {len(image_files)}")
    if errors:
        print()
        print("Errors (could not read metadata):")
        for name, err in errors:
            print(f"  {name}: {err}")


if __name__ == "__main__":
    main()
