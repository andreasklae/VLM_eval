"""
Human Evaluation UI for Image Recognition
==========================================
Local Flask server that serves a web UI for manually evaluating
image recognition model outputs against ground truth.

Usage:
    cd testing/Image_search/Evaluation
    pip install -r requirements-ui.txt
    python evaluation_ui.py

Then open http://localhost:5001 in your browser.
"""

import json
import io
from datetime import date
from pathlib import Path
from flask import Flask, jsonify, request, send_file, send_from_directory, abort

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent  # .../Evaluation/
IMAGE_SEARCH_DIR = BASE_DIR.parent          # .../Image_search/
INPUTS_DIR = IMAGE_SEARCH_DIR / "results" / ".eval_work" / "inputs"
IMAGES_DIR = IMAGE_SEARCH_DIR / "test_images"
OUTPUT_FILE = BASE_DIR / "human_evaluation.json"

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder="static", static_url_path="/static")

# ---------------------------------------------------------------------------
# Image cache (HEIC → JPEG bytes, kept in memory)
# ---------------------------------------------------------------------------
_image_cache: dict[str, bytes] = {}

# ---------------------------------------------------------------------------
# Eval-input index  {image_id (int) -> file path}
# ---------------------------------------------------------------------------
_input_index: dict[int, Path] = {}
_filename_cache: dict[int, str] = {}  # image_id → filename (cached)


def _build_input_index():
    """Scan the inputs directory and build an index of image_id → file path."""
    global _input_index, _filename_cache
    _input_index = {}
    _filename_cache = {}
    for p in sorted(INPUTS_DIR.glob("eval_input_*.json")):
        stem = p.stem  # eval_input_001
        try:
            image_id = int(stem.split("_")[-1])
            _input_index[image_id] = p
            # Cache filename to avoid reading every file on /api/images
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            _filename_cache[image_id] = data.get("filename", "")
        except (ValueError, json.JSONDecodeError):
            continue


def _read_output() -> dict:
    """Read the output JSON file, or create a fresh skeleton."""
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "metadata": {
            "created": str(date.today()),
            "last_updated": str(date.today()),
            "evaluator": "human",
            "total_images": len(_input_index),
            "evaluated_count": 0,
        },
        "images": {},
    }


def _write_output(data: dict):
    """Write the output JSON file atomically."""
    data["metadata"]["last_updated"] = str(date.today())
    # Count evaluated
    data["metadata"]["evaluated_count"] = sum(
        1 for v in data["images"].values() if v.get("status") == "complete"
    )
    data["metadata"]["total_images"] = len(_input_index)
    tmp = OUTPUT_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(OUTPUT_FILE)


def _find_image_file(filename: str) -> Path | None:
    """Find the actual image file on disk (case-insensitive extension)."""
    # Try exact match first
    candidate = IMAGES_DIR / filename
    if candidate.exists():
        return candidate
    # Try case-insensitive
    stem = Path(filename).stem
    for ext in [".jpg", ".jpeg", ".png", ".heic", ".heif", ".gif", ".bmp", ".webp"]:
        for case_ext in [ext, ext.upper()]:
            candidate = IMAGES_DIR / (stem + case_ext)
            if candidate.exists():
                return candidate
    return None


def _serve_image_bytes(image_path: Path) -> tuple[bytes, str]:
    """Return (bytes, mimetype) for an image, converting HEIC if needed."""
    suffix = image_path.suffix.lower()
    cache_key = str(image_path)

    if suffix in (".heic", ".heif"):
        if cache_key in _image_cache:
            return _image_cache[cache_key], "image/jpeg"
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
        except ImportError:
            abort(500, "pillow-heif not installed; cannot serve HEIC images")
        from PIL import Image
        img = Image.open(image_path)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=85)
        jpeg_bytes = buf.getvalue()
        _image_cache[cache_key] = jpeg_bytes
        return jpeg_bytes, "image/jpeg"

    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".webp": "image/webp",
    }
    mime = mime_map.get(suffix, "application/octet-stream")
    return image_path.read_bytes(), mime


# ===================================================================
# Routes
# ===================================================================

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/images")
def api_images():
    """Return list of all image IDs with evaluation status."""
    output = _read_output()
    images = []
    for image_id in sorted(_input_index.keys()):
        entry = output["images"].get(str(image_id))
        status = entry.get("status", "pending") if entry else "pending"
        images.append({
            "image_id": image_id,
            "filename": _filename_cache.get(image_id, ""),
            "status": status,
        })
    return jsonify(images)


@app.route("/api/image/<int:image_id>")
def api_image(image_id: int):
    """Return eval_input data + any existing evaluation for one image."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    with open(_input_index[image_id], "r", encoding="utf-8") as f:
        eval_input = json.load(f)
    output = _read_output()
    existing_eval = output["images"].get(str(image_id))
    return jsonify({
        "eval_input": eval_input,
        "existing_eval": existing_eval,
    })


@app.route("/api/image/<int:image_id>/photo")
def api_image_photo(image_id: int):
    """Serve the test image (converting HEIC to JPEG if needed)."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    filename = _filename_cache.get(image_id, "")
    image_path = _find_image_file(filename)
    if image_path is None:
        abort(404, f"Image file not found: {filename}")
    img_bytes, mime = _serve_image_bytes(image_path)
    return send_file(io.BytesIO(img_bytes), mimetype=mime)


@app.route("/api/image/<int:image_id>/evaluate", methods=["POST"])
def api_evaluate(image_id: int):
    """Save evaluation scores for one image."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    payload = request.get_json(force=True)
    output = _read_output()
    entry = {
        "image_id": image_id,
        "filename": _filename_cache.get(image_id, ""),
        "status": payload.get("status", "complete"),
        "evaluator_notes": payload.get("evaluator_notes", ""),
        "ground_truth": payload.get("ground_truth"),
        "evals": payload.get("evals", []),
    }
    output["images"][str(image_id)] = entry
    _write_output(output)
    return jsonify({"ok": True, "image_id": image_id})


def _read_eval_input(image_id: int) -> dict:
    """Read an eval_input file."""
    with open(_input_index[image_id], "r", encoding="utf-8") as f:
        return json.load(f)


def _write_eval_input(image_id: int, data: dict):
    """Write an eval_input file atomically."""
    path = _input_index[image_id]
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


@app.route("/api/image/<int:image_id>/ground-truth", methods=["POST"])
def api_ground_truth(image_id: int):
    """Add a ground truth entry — writes directly to the eval_input file."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    payload = request.get_json(force=True)
    gt_type = payload.get("type")  # "location" or "entity"
    entry_data = payload.get("data", {})
    entry_data["added_by"] = "human_evaluator"

    # Write to eval_input file
    eval_input = _read_eval_input(image_id)
    gt = eval_input.setdefault("ground_truth", {})
    if gt_type == "location":
        gt.setdefault("locations", []).append(entry_data)
    elif gt_type == "entity":
        gt.setdefault("entities", []).append(entry_data)
    else:
        abort(400, "type must be 'location' or 'entity'")
    _write_eval_input(image_id, eval_input)

    return jsonify({
        "ok": True,
        "ground_truth": gt,
    })


@app.route("/api/image/<int:image_id>/ground-truth/entity/<int:idx>", methods=["PUT"])
def api_update_gt_entity(image_id: int, idx: int):
    """Update a ground truth entity field (e.g. max_specificity) in the eval_input file."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    payload = request.get_json(force=True)

    eval_input = _read_eval_input(image_id)
    entities = eval_input.get("ground_truth", {}).get("entities", [])
    if idx < 0 or idx >= len(entities):
        abort(404, f"Entity index {idx} out of range (have {len(entities)})")

    # Update only the fields provided
    for key, value in payload.items():
        entities[idx][key] = value
    _write_eval_input(image_id, eval_input)

    return jsonify({"ok": True, "entity": entities[idx]})


@app.route("/api/image/<int:image_id>/ground-truth", methods=["PATCH"])
def api_patch_gt(image_id: int):
    """Update top-level ground truth fields (e.g. image_categories)."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    payload = request.get_json(force=True)
    eval_input = _read_eval_input(image_id)
    gt = eval_input.setdefault("ground_truth", {})
    for key, value in payload.items():
        gt[key] = value
    _write_eval_input(image_id, eval_input)
    return jsonify({"ok": True})


@app.route("/api/image/<int:image_id>/ground-truth/location/<int:idx>", methods=["PUT"])
def api_update_gt_location(image_id: int, idx: int):
    """Update a ground truth location field in the eval_input file."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    payload = request.get_json(force=True)

    eval_input = _read_eval_input(image_id)
    locations = eval_input.get("ground_truth", {}).get("locations", [])
    if idx < 0 or idx >= len(locations):
        abort(404, f"Location index {idx} out of range (have {len(locations)})")

    for key, value in payload.items():
        locations[idx][key] = value
    _write_eval_input(image_id, eval_input)

    return jsonify({"ok": True, "location": locations[idx]})


@app.route("/api/image/<int:image_id>/ground-truth/entity/<int:idx>", methods=["DELETE"])
def api_delete_gt_entity(image_id: int, idx: int):
    """Delete a ground truth entity from the eval_input file."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    eval_input = _read_eval_input(image_id)
    entities = eval_input.get("ground_truth", {}).get("entities", [])
    if idx < 0 or idx >= len(entities):
        abort(404, f"Entity index {idx} out of range (have {len(entities)})")
    removed = entities.pop(idx)
    _write_eval_input(image_id, eval_input)
    return jsonify({"ok": True, "removed": removed})


@app.route("/api/image/<int:image_id>/ground-truth/location/<int:idx>", methods=["DELETE"])
def api_delete_gt_location(image_id: int, idx: int):
    """Delete a ground truth location from the eval_input file."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    eval_input = _read_eval_input(image_id)
    locations = eval_input.get("ground_truth", {}).get("locations", [])
    if idx < 0 or idx >= len(locations):
        abort(404, f"Location index {idx} out of range (have {len(locations)})")
    removed = locations.pop(idx)
    _write_eval_input(image_id, eval_input)
    return jsonify({"ok": True, "removed": removed})


@app.route("/api/image/<int:image_id>/difficulty", methods=["PUT"])
def api_set_difficulty(image_id: int):
    """Set difficulty_with_gps or difficulty_without_gps on the ground truth."""
    if image_id not in _input_index:
        abort(404, f"Image {image_id} not found")
    payload = request.get_json(force=True)
    field = payload.get("field")
    value = payload.get("value")
    if field not in ("difficulty_with_gps", "difficulty_without_gps"):
        abort(400, f"Invalid field: {field}")
    if value not in ("easy", "medium", "hard"):
        abort(400, f"Invalid value: {value}")

    eval_input = _read_eval_input(image_id)
    gt = eval_input.setdefault("ground_truth", {})
    gt[field] = value
    _write_eval_input(image_id, eval_input)
    return jsonify({"ok": True, field: value})


@app.route("/api/progress")
def api_progress():
    """Return evaluation progress."""
    output = _read_output()
    total = len(_input_index)
    evaluated = sum(
        1 for v in output["images"].values() if v.get("status") == "complete"
    )
    skipped = sum(
        1 for v in output["images"].values() if v.get("status") == "skipped"
    )
    return jsonify({
        "total": total,
        "evaluated": evaluated,
        "skipped": skipped,
        "remaining": total - evaluated - skipped,
    })


# ===================================================================
# Main
# ===================================================================
if __name__ == "__main__":
    _build_input_index()
    print(f"Found {len(_input_index)} eval input files in {INPUTS_DIR}")
    print(f"Test images directory: {IMAGES_DIR}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"\nStarting server at http://localhost:5001")
    app.run(host="127.0.0.1", port=5001, debug=True)
