#!/usr/bin/env python3
"""
Produce per-image evaluation input files from ground truth and master JSONL.

Reads ground_truth.json and batch_test_results_1_master.jsonl, and writes one
eval_input_{image_id:03d}.json per image to results/.eval_work/inputs/.
Also writes manifest.json with image_id, filename, and approximate character
count for context-aware batch assignment.

Usage:
    python scripts/preprocess_for_evaluation.py
"""

import json
import re
import sys
from pathlib import Path

# Paths relative to testing/Image_search
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
GT_PATH = ROOT / "results" / "ground_truth.json"
JSONL_PATH = ROOT / "results" / "batch_test_results_1_master.jsonl"
OUTPUT_DIR = ROOT / "results" / ".eval_work" / "inputs"
MANIFEST_PATH = ROOT / "results" / ".eval_work" / "manifest.json"


def load_ground_truth(path: Path) -> list[dict]:
    """Load ground truth array from JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if "ground_truth" in data:
        return data["ground_truth"]
    return data


def parse_jsonl_pretty(path: Path) -> list[dict]:
    """Parse a file of pretty-printed JSON objects (one per block, separated by newline)."""
    content = path.read_text(encoding="utf-8")
    results = []
    i = 0
    n = len(content)
    while i < n:
        # Find start of next object
        brace = content.find("{", i)
        if brace == -1:
            break
        depth = 0
        j = brace
        in_string = False
        escape = False
        quote_char = None
        while j < n:
            c = content[j]
            if in_string:
                if escape:
                    escape = False
                elif c == "\\":
                    escape = True
                elif c == quote_char:
                    in_string = False
            else:
                if c in '"\'':
                    in_string = True
                    quote_char = c
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        chunk = content[brace : j + 1]
                        try:
                            results.append(json.loads(chunk))
                        except json.JSONDecodeError as e:
                            raise RuntimeError(f"JSON parse error at position {brace}: {e}") from e
                        j += 1
                        break
            j += 1
        i = j
    return results


def slim_run(record: dict) -> dict:
    """Keep only fields needed for evaluation; strip bulk."""
    out = {
        "image_filename": record.get("image_filename"),
        "use_gps": record.get("use_gps"),
        "approaches": [],
    }
    for ap in record.get("approaches", []):
        details = ap.get("details") or {}
        slim_details = {
            "approach": details.get("approach") or ap.get("approach"),
            "description": details.get("description"),
            "photographer_location": details.get("photographer_location") or [],
            "subject_location": details.get("subject_location") or [],
            "entities": details.get("entities") or [],
            "landmark_name": details.get("landmark_name"),
        }
        out["approaches"].append({"approach": slim_details["approach"], "details": slim_details})
    return out


def main() -> None:
    if not GT_PATH.exists():
        print(f"Error: {GT_PATH} not found", file=sys.stderr)
        sys.exit(1)
    if not JSONL_PATH.exists():
        print(f"Error: {JSONL_PATH} not found", file=sys.stderr)
        sys.exit(1)

    gt_list = load_ground_truth(GT_PATH)
    print(f"Loaded {len(gt_list)} ground truth images", file=sys.stderr)

    print("Parsing JSONL (this may take a moment)...", file=sys.stderr)
    records = parse_jsonl_pretty(JSONL_PATH)
    print(f"Parsed {len(records)} JSONL records", file=sys.stderr)

    # Group by image_filename -> list of records (typically 2: gps true, gps false)
    by_filename: dict[str, list[dict]] = {}
    for r in records:
        fn = r.get("image_filename")
        if not fn:
            continue
        by_filename.setdefault(fn, []).append(r)

    # Extract GPS metadata per image from the use_gps=true run
    gps_by_filename: dict[str, dict] = {}
    for fn, recs in by_filename.items():
        for r in recs:
            if r.get("use_gps") and r.get("metadata"):
                meta = r["metadata"]
                lat = meta.get("gps_latitude")
                lon = meta.get("gps_longitude")
                if lat is not None and lon is not None:
                    gps_entry: dict = {
                        "gps_latitude": lat,
                        "gps_longitude": lon,
                    }
                    loc = meta.get("location")
                    if loc:
                        gps_entry["reverse_geocoded"] = {
                            "formatted_address": loc.get("formatted_address"),
                            "city": loc.get("city"),
                            "county": loc.get("county"),
                            "country": loc.get("country"),
                        }
                    gps_by_filename[fn] = gps_entry
                    break

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []

    for gt in gt_list:
        image_id = gt.get("image_id")
        filename = gt.get("filename")
        if image_id is None or not filename:
            continue
        runs = by_filename.get(filename, [])
        if len(runs) == 0:
            print(f"Warning: no model runs for image_id={image_id} filename={filename}", file=sys.stderr)
        # Sort so use_gps true first, then false
        runs_sorted = sorted(runs, key=lambda r: (not r.get("use_gps", False), r.get("image_filename", "")))

        gt_section: dict = {
            "description": gt.get("description"),
            "photographer_description": gt.get("photographer_description"),
            "locations": gt.get("locations", []),
            "entities": gt.get("entities", []),
            "scene_type": gt.get("scene_type", []),
            "key_visual_elements": gt.get("key_visual_elements", []),
            "max_specificity": gt.get("max_specificity"),
            "difficulty": gt.get("difficulty"),
            "notes": gt.get("notes"),
        }
        # Add GPS metadata as ground truth if available
        gps = gps_by_filename.get(filename)
        if gps:
            gt_section["gps_metadata"] = gps
        else:
            gt_section["gps_metadata"] = None

        payload = {
            "image_id": image_id,
            "filename": filename,
            "ground_truth": gt_section,
            "model_runs": [slim_run(r) for r in runs_sorted],
        }

        out_path = OUTPUT_DIR / f"eval_input_{image_id:03d}.json"
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        char_count = len(json.dumps(payload, ensure_ascii=False))
        manifest.append({"image_id": image_id, "filename": filename, "approx_chars": char_count})

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(gt_list)} input files to {OUTPUT_DIR}", file=sys.stderr)
    print(f"Wrote manifest to {MANIFEST_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
