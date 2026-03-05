#!/usr/bin/env python3
"""
Renumber images to remove gaps in numbering (e.g., 1.jpg, 3.jpg, 5.jpg -> 1.jpg, 2.jpg, 3.jpg).
"""

import re
import sys
from pathlib import Path


def extract_number(filename: str) -> int:
    """Extract number from filename like '1.jpg' or '123.heic'."""
    match = re.match(r'^(\d+)\.', filename)
    if match:
        return int(match.group(1))
    return 0


def main():
    """Main function to renumber images."""
    test_images_dir = Path(__file__).parent / "test_images"
    
    if not test_images_dir.exists():
        print(f"Error: Directory not found: {test_images_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Get all image files (exclude .DS_Store and markdown files)
    image_extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG', '.heic', '.HEIC', '.png', '.PNG'}
    image_files = [
        f for f in test_images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in {ext.lower() for ext in image_extensions}
        and f.name != 'image_descriptions.md'
        and (re.match(r'^\d+\.', f.name) or re.match(r'^temp_\d+\.', f.name))  # Files starting with number or temp_number
    ]
    
    # If we have temp files, use those; otherwise use numbered files
    temp_files_exist = any(re.match(r'^temp_\d+\.', f.name) for f in image_files)
    if temp_files_exist:
        # Extract number from temp files
        image_files = [f for f in image_files if re.match(r'^temp_\d+\.', f.name)]
        image_files.sort(key=lambda f: extract_number(f.name.replace('temp_', '')))
    else:
        # Extract number from regular numbered files
        image_files = [f for f in image_files if re.match(r'^\d+\.', f.name)]
        image_files.sort(key=lambda f: extract_number(f.name))
    
    if not image_files:
        print("No numbered image files found.", file=sys.stderr)
        sys.exit(1)
    
    # Sort by current number
    image_files.sort(key=lambda f: extract_number(f.name))
    
    print(f"Found {len(image_files)} image files.", file=sys.stderr)
    print("Renumbering to remove gaps...", file=sys.stderr)
    
    # If files are already temp files, skip to final renaming
    if temp_files_exist:
        print("Found temp files from previous run. Renaming directly to final numbers...", file=sys.stderr)
        for idx, image_file in enumerate(image_files, start=1):
            ext = image_file.suffix.lower()
            # Normalize extension
            if ext in {'.jpeg', '.jpg'}:
                new_ext = '.jpg'
            elif ext in {'.heic', '.heif'}:
                new_ext = '.heic'
            else:
                new_ext = ext
            
            final_name = f"{idx}{new_ext}"
            final_path = test_images_dir / final_name
            try:
                image_file.rename(final_path)
                print(f"  {image_file.name} -> {final_name}", file=sys.stderr)
            except Exception as e:
                print(f"Error renaming {image_file.name}: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        # Create temporary names first to avoid conflicts
        temp_files = []
        for idx, image_file in enumerate(image_files, start=1):
            ext = image_file.suffix.lower()
            # Normalize extension
            if ext in {'.jpeg', '.jpg'}:
                new_ext = '.jpg'
            elif ext in {'.heic', '.heif'}:
                new_ext = '.heic'
            else:
                new_ext = ext
            
            new_name = f"temp_{idx}{new_ext}"
            new_path = test_images_dir / new_name
            temp_files.append((image_file, new_path, idx, new_ext))
        
        # First pass: rename to temporary names
        print("\nStep 1: Renaming to temporary names...", file=sys.stderr)
        for original_path, temp_path, idx, ext in temp_files:
            try:
                original_path.rename(temp_path)
                print(f"  {original_path.name} -> {temp_path.name}", file=sys.stderr)
            except Exception as e:
                print(f"Error renaming {original_path.name}: {e}", file=sys.stderr)
                sys.exit(1)
        
        # Second pass: rename from temp to final names
        print("\nStep 2: Renaming to final sequential numbers...", file=sys.stderr)
        for _, temp_path, idx, ext in temp_files:
            final_name = f"{idx}{ext}"
            final_path = test_images_dir / final_name
            try:
                if temp_path.exists():
                    temp_path.rename(final_path)
                    print(f"  {temp_path.name} -> {final_name}", file=sys.stderr)
                else:
                    print(f"Warning: {temp_path.name} does not exist, skipping", file=sys.stderr)
            except Exception as e:
                print(f"Error renaming {temp_path.name}: {e}", file=sys.stderr)
                sys.exit(1)
    
    print(f"\nSuccessfully renumbered {len(image_files)} files.", file=sys.stderr)
    print(f"Files are now numbered from 1 to {len(image_files)} with no gaps.", file=sys.stderr)


if __name__ == "__main__":
    main()
