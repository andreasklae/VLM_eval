#!/usr/bin/env python3
"""
Rename images by their metadata date (oldest = 1, newest = highest number).
Also creates a markdown template for image descriptions.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add backend to path to import metadata extraction
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from image_recognition.metadata import extract_metadata


def parse_datetime(datetime_str: str | None) -> datetime | None:
    """Parse datetime string from EXIF metadata."""
    if not datetime_str:
        return None
    
    # Try common EXIF datetime formats
    formats = [
        "%Y:%m:%d %H:%M:%S",  # Standard EXIF format
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y:%m:%d %H:%M:%S.%f",  # With microseconds
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    
    return None


def get_image_date(image_path: Path) -> datetime | None:
    """Extract date from image metadata."""
    try:
        image_data = image_path.read_bytes()
        metadata = extract_metadata(image_data)
        
        if metadata.datetime_original:
            return parse_datetime(metadata.datetime_original)
        
        return None
    except Exception as e:
        print(f"Warning: Could not extract date from {image_path.name}: {e}", file=sys.stderr)
        return None


def main():
    """Main function to rename images and create template."""
    test_images_dir = Path(__file__).parent / "test_images"
    
    if not test_images_dir.exists():
        print(f"Error: Directory not found: {test_images_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Get all image files (exclude .DS_Store and template file)
    image_extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG', '.heic', '.HEIC', '.png', '.PNG'}
    image_files = [
        f for f in test_images_dir.iterdir()
        if f.is_file() and f.suffix in image_extensions and f.name != 'image_descriptions.md'
    ]
    
    if not image_files:
        print("No image files found.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(image_files)} image files.", file=sys.stderr)
    print("Extracting dates from metadata...", file=sys.stderr)
    
    # Extract dates and create list of (date, original_path, extension)
    images_with_dates = []
    for image_path in image_files:
        date = get_image_date(image_path)
        # Use a very old date as fallback if no date found
        fallback_date = datetime(1900, 1, 1)
        images_with_dates.append((date or fallback_date, image_path, image_path.suffix.lower()))
    
    # Sort by date (oldest first = lower number)
    images_with_dates.sort(key=lambda x: x[0])
    
    print(f"Sorting images by date (oldest to newest)...", file=sys.stderr)
    
    # Create mapping of old names to new names
    rename_mapping = []
    template_entries = []
    
    for idx, (date, original_path, ext) in enumerate(images_with_dates, start=1):
        # Normalize extension (use .jpg for jpeg, .heic for heic)
        if ext in {'.jpeg', '.jpg'}:
            new_ext = '.jpg'
        elif ext in {'.heic', '.heif'}:
            new_ext = '.heic'
        else:
            new_ext = ext
        
        new_name = f"{idx}{new_ext}"
        new_path = test_images_dir / new_name
        
        # Store mapping
        rename_mapping.append((original_path, new_path, date))
        
        # Create template entry
        date_str = date.strftime("%Y-%m-%d %H:%M:%S") if date and date.year > 1900 else "Unknown date"
        template_entries.append({
            'number': idx,
            'old_name': original_path.name,
            'new_name': new_name,
            'date': date_str,
            'extension': new_ext
        })
    
    # Rename files
    print(f"\nRenaming {len(rename_mapping)} files...", file=sys.stderr)
    renamed_count = 0
    
    for original_path, new_path, date in rename_mapping:
        if original_path == new_path:
            continue  # Already has correct name
        
        # Check if target already exists
        if new_path.exists() and new_path != original_path:
            print(f"Warning: Target exists, skipping: {new_path.name}", file=sys.stderr)
            continue
        
        try:
            original_path.rename(new_path)
            renamed_count += 1
            date_str = date.strftime("%Y-%m-%d") if date and date.year > 1900 else "no date"
            print(f"  {original_path.name} -> {new_path.name} ({date_str})", file=sys.stderr)
        except Exception as e:
            print(f"Error renaming {original_path.name}: {e}", file=sys.stderr)
    
    print(f"\nRenamed {renamed_count} files.", file=sys.stderr)
    
    # Create markdown template
    template_path = test_images_dir / "image_descriptions.md"
    
    print(f"\nCreating template file: {template_path}", file=sys.stderr)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write("# Image Descriptions\n\n")
        f.write("This file contains descriptions of test images for comparison with model outputs.\n\n")
        f.write("Format: Image number, original filename, date, and description.\n\n")
        f.write("---\n\n")
        
        for entry in template_entries:
            f.write(f"## Image {entry['number']}\n\n")
            f.write(f"**File:** `{entry['new_name']}`\n")
            f.write(f"**Original:** `{entry['old_name']}`\n")
            f.write(f"**Date:** {entry['date']}\n\n")
            f.write("**Description:**\n")
            f.write("<!-- Fill in description here -->\n\n")
            f.write("---\n\n")
    
    print(f"Template created with {len(template_entries)} entries.", file=sys.stderr)
    print(f"\nDone! Edit {template_path} to add descriptions.", file=sys.stderr)


if __name__ == "__main__":
    main()
