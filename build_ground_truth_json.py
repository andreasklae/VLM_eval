#!/usr/bin/env python3
"""
Parse ground truth markdown files into a structured JSON file.

Reads all per-image ground truth files from results/ground_truth_per_image/
and produces a single JSON file with a structure comparable to the backend's
recognition output, enabling automated comparison.

Usage:
    python build_ground_truth_json.py
"""

import json
import re
import sys
from pathlib import Path


GT_DIR = Path(__file__).parent / "results" / "ground_truth_per_image"
OUTPUT_PATH = Path(__file__).parent / "results" / "ground_truth.json"


def parse_ground_truth_file(path: Path) -> dict | None:
    """Parse a single ground truth markdown file into a structured dict."""
    text = path.read_text(encoding="utf-8")

    # --- Extract image_id and filename from the ### Image N header ---
    m_header = re.search(r"### Image (\d+)", text)
    if not m_header:
        return None
    image_id = int(m_header.group(1))

    m_file = re.search(r"\*\*File:\*\*\s*`([^`]+)`", text)
    filename = m_file.group(1) if m_file else path.name

    # --- Photographer description (free text between "## Photographer Description" and "---") ---
    m_photo_desc = re.search(
        r"## Photographer Description\s*\n\s*\n(.*?)(?=\n---)", text, re.DOTALL
    )
    photographer_description = m_photo_desc.group(1).strip() if m_photo_desc else None

    # --- Ground truth description ---
    m_gt_desc = re.search(
        r"#### Ground Truth Description\s*\n(.*?)(?=\n####|\n---)", text, re.DOTALL
    )
    description = m_gt_desc.group(1).strip() if m_gt_desc else None

    # --- Landmarks ---
    entities = []
    m_landmarks_block = re.search(
        r"\*\*Landmarks:\*\*\s*\n(.*?)(?=\n\*\*Location|\n####)", text, re.DOTALL
    )
    if m_landmarks_block:
        block = m_landmarks_block.group(1).strip()
        # Skip "None" entries
        if not re.match(r"^-?\s*None", block, re.IGNORECASE):
            for line in block.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Strip markdown checkbox and leading dash
                cleaned = re.sub(r"^-\s*(\[.\]\s*)?", "", line).strip()
                if cleaned and not re.match(r"^None", cleaned, re.IGNORECASE):
                    # Check for parenthetical notes like "(edge, bonus)"
                    notes = None
                    m_notes = re.match(r"^(.*?)\s*\(([^)]+)\)\s*$", cleaned)
                    if m_notes:
                        name = m_notes.group(1).strip()
                        notes = m_notes.group(2).strip()
                    else:
                        name = cleaned
                    entities.append({
                        "name": name,
                        "type": "landmark",
                        "notes": notes,
                    })

    # --- Location ---
    locations = []
    m_loc_block = re.search(
        r"\*\*Location:\*\*\s*\n(.*?)(?=\n\*\*Scene Type|\n####)", text, re.DOTALL
    )
    if m_loc_block:
        loc_block = m_loc_block.group(1).strip()
        hierarchy = {}
        for line in loc_block.split("\n"):
            line = line.strip()
            m_field = re.match(r"^-\s*(Country|Region|City|Exact):\s*(.*)", line)
            if m_field:
                key = m_field.group(1).lower()
                value = m_field.group(2).strip()
                if value:
                    hierarchy[key] = value

        if hierarchy:
            # Build a canonical location name from most specific to least
            location_name_parts = []
            for key in ("exact", "city", "region", "country"):
                if key in hierarchy:
                    location_name_parts.append(hierarchy[key])
            location_name = ", ".join(location_name_parts) if location_name_parts else None

            locations.append({
                "name": location_name,
                "hierarchy": hierarchy,
            })

    # --- Scene type ---
    scene_type = []
    m_scene = re.search(r"\*\*Scene Type:\*\*\s*(.*)", text)
    if m_scene:
        raw = m_scene.group(1).strip()
        scene_type = [s.strip() for s in raw.split(",") if s.strip()]

    # --- Key visual elements ---
    key_visual_elements = []
    m_kve_block = re.search(
        r"\*\*Key Visual Elements:\*\*\s*\n(.*?)(?=\n\*\*Max Specificity|\n####|\n---)",
        text,
        re.DOTALL,
    )
    if m_kve_block:
        for line in m_kve_block.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("-"):
                element = line.lstrip("- ").strip()
                if element:
                    key_visual_elements.append(element)

    # --- Max specificity ---
    max_specificity = None
    m_spec = re.search(r"\*\*Max Specificity:\*\*\s*(.*)", text)
    if m_spec:
        max_specificity = m_spec.group(1).strip()

    # --- Difficulty ---
    difficulty = None
    m_diff = re.search(r"\*\*Difficulty:\*\*\s*(.*)", text)
    if m_diff:
        difficulty = m_diff.group(1).strip()

    # --- Notes ---
    notes = None
    m_notes_section = re.search(r"\*\*Notes:\*\*\s*(.*?)(?=\n---|\Z)", text, re.DOTALL)
    if m_notes_section:
        notes = m_notes_section.group(1).strip() or None

    return {
        "image_id": image_id,
        "filename": filename,
        "description": description,
        "photographer_description": photographer_description,
        "locations": locations,
        "entities": entities,
        "scene_type": scene_type,
        "key_visual_elements": key_visual_elements,
        "max_specificity": max_specificity,
        "difficulty": difficulty,
        "notes": notes,
    }


def main():
    if not GT_DIR.exists():
        print(f"Ground truth directory not found: {GT_DIR}", file=sys.stderr)
        sys.exit(1)

    files = sorted(GT_DIR.glob("image_*.md"))
    print(f"Found {len(files)} ground truth files in {GT_DIR}", file=sys.stderr)

    ground_truth = []
    errors = []

    for f in files:
        try:
            entry = parse_ground_truth_file(f)
            if entry is not None:
                ground_truth.append(entry)
            else:
                errors.append(f"Could not parse: {f.name}")
        except Exception as exc:
            errors.append(f"Error parsing {f.name}: {exc}")

    # Sort by image_id
    ground_truth.sort(key=lambda x: x["image_id"])

    output = {
        "dataset_info": {
            "total_images": len(ground_truth),
            "source_directory": str(GT_DIR),
            "description": "Structured ground truth for image recognition evaluation, "
                           "parsed from per-image markdown files.",
        },
        "ground_truth": ground_truth,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(ground_truth)} entries to {OUTPUT_PATH}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)

    # Quick stats
    with_entities = sum(1 for g in ground_truth if g["entities"])
    with_locations = sum(1 for g in ground_truth if g["locations"])
    print(f"\nStats:", file=sys.stderr)
    print(f"  With entities (landmarks): {with_entities}/{len(ground_truth)}", file=sys.stderr)
    print(f"  With locations: {with_locations}/{len(ground_truth)}", file=sys.stderr)


if __name__ == "__main__":
    main()
