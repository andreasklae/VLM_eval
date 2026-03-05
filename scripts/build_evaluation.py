#!/usr/bin/env python3
"""
Build full evaluation JSON from compact agent scores + eval_input data.

Reads scores_{id}.json from .eval_work/scores/, resolves all indices against
the corresponding eval_input_{id}.json, validates scoring values, and writes
eval_{id}.json to .eval_work/outputs/ with a hardcoded, guaranteed structure.

Usage:
    python scripts/build_evaluation.py                  # process all scores
    python scripts/build_evaluation.py --image-id 16    # process one image
    python scripts/build_evaluation.py --validate-only   # only validate, don't write
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
INPUTS_DIR = ROOT / "results" / ".eval_work" / "inputs"
SCORES_DIR = ROOT / "results" / ".eval_work" / "scores"
OUTPUTS_DIR = ROOT / "results" / ".eval_work" / "outputs"

# ── Constants ────────────────────────────────────────────────────────────────

APPROACH_NAMES = [
    "GPT Vision Direct (strong)",
    "GPT Vision Direct (fast)",
    "GPT Vision + Search (strong)",
    "GPT Vision + Search (fast)",
    "Gemini Vision (strong)",
    "Gemini Vision (fast)",
    "Google Cloud Vision",
]

VALID_CORRECTNESS = {-1.0, -0.5, 0.0, 0.5, 1.0}
VALID_SPECIFICITY = {1, 2, 3, 4, 5}
VALID_DESC_SCORES = {0, 1, 2, 3, 4}
VALID_REF_TYPES = {"photographer_position", "depicted_subject", "ambiguous_or_unspecified"}
VALID_SOURCES = {"photographer_location", "subject_location"}

CLOUD_VISION_INDEX = 6  # Google Cloud Vision is approach_index 6


def get_approach_by_canonical_index(run: dict, ai: int):
    """Resolve approach by canonical name so input order can differ from APPROACH_NAMES."""
    name = APPROACH_NAMES[ai]
    for ap in run.get("approaches", []):
        if ap.get("approach") == name:
            return ap
    return None


# ── Validation helpers ───────────────────────────────────────────────────────

def validate_scores(scores: dict, eval_input: dict) -> list[str]:
    """Validate a compact scores file. Return list of error messages."""
    errors: list[str] = []
    image_id = scores.get("image_id")
    if image_id != eval_input.get("image_id"):
        errors.append(f"image_id mismatch: scores={image_id}, input={eval_input.get('image_id')}")

    mes = scores.get("max_entity_specificity")
    if mes is None or mes not in VALID_SPECIFICITY:
        errors.append(f"max_entity_specificity must be 1-5, got {mes!r}")

    evals = scores.get("evals", [])
    model_runs = eval_input.get("model_runs", [])

    for i, ev in enumerate(evals):
        prefix = f"evals[{i}]"
        ri = ev.get("run_index")
        ai = ev.get("approach_index")

        if ri is None or not isinstance(ri, int) or ri < 0:
            errors.append(f"{prefix}.run_index invalid: {ri!r}")
            continue
        if ri >= len(model_runs):
            errors.append(f"{prefix}.run_index={ri} out of range (only {len(model_runs)} runs)")
            continue
        if ai is None or not isinstance(ai, int) or ai < 0 or ai > 6:
            errors.append(f"{prefix}.approach_index must be 0-6, got {ai!r}")
            continue

        run = model_runs[ri]
        approach_data = get_approach_by_canonical_index(run, ai)
        if approach_data is None:
            errors.append(f"{prefix}.approach_index={ai} ({APPROACH_NAMES[ai]!r}) not found in run approaches")
            continue
        details = approach_data.get("details", {})

        # Validate location groups
        for j, lg in enumerate(ev.get("location_groups", [])):
            lp = f"{prefix}.location_groups[{j}]"
            src = lg.get("source")
            if src not in VALID_SOURCES:
                errors.append(f"{lp}.source must be 'photographer_location' or 'subject_location', got {src!r}")
            else:
                src_array = details.get(src, [])
                for mi in lg.get("model_indices", []):
                    if not isinstance(mi, int) or mi < 0 or mi >= len(src_array):
                        errors.append(f"{lp}.model_indices contains {mi}, but {src} has {len(src_array)} entries")
            rt = lg.get("ref_type")
            if rt not in VALID_REF_TYPES:
                errors.append(f"{lp}.ref_type must be one of {VALID_REF_TYPES}, got {rt!r}")
            sp = lg.get("specificity")
            if sp not in VALID_SPECIFICITY:
                errors.append(f"{lp}.specificity must be 1-5, got {sp!r}")
            co = lg.get("correctness")
            if co not in VALID_CORRECTNESS:
                errors.append(f"{lp}.correctness must be in {VALID_CORRECTNESS}, got {co!r}")
            if not isinstance(lg.get("reason", ""), str):
                errors.append(f"{lp}.reason must be a string")
            gi = lg.get("gt_index")
            gt_locs = eval_input.get("ground_truth", {}).get("locations", [])
            if gi is not None:
                if not isinstance(gi, int) or gi < 0 or gi >= len(gt_locs):
                    errors.append(f"{lp}.gt_index={gi} out of range (GT has {len(gt_locs)} locations)")
            if not isinstance(lg.get("flag", False), bool):
                errors.append(f"{lp}.flag must be boolean")

        # Validate entity groups
        for j, eg in enumerate(ev.get("entity_groups", [])):
            ep = f"{prefix}.entity_groups[{j}]"
            ent_array = details.get("entities", [])
            for mi in eg.get("model_indices", []):
                if not isinstance(mi, int) or mi < 0 or mi >= len(ent_array):
                    errors.append(f"{ep}.model_indices contains {mi}, but entities has {len(ent_array)} entries")
            sp = eg.get("specificity")
            if sp not in VALID_SPECIFICITY:
                errors.append(f"{ep}.specificity must be 1-5, got {sp!r}")
            co = eg.get("correctness")
            if co not in VALID_CORRECTNESS:
                errors.append(f"{ep}.correctness must be in {VALID_CORRECTNESS}, got {co!r}")
            if not isinstance(eg.get("reason", ""), str):
                errors.append(f"{ep}.reason must be a string")
            gi = eg.get("gt_index")
            gt_ents = eval_input.get("ground_truth", {}).get("entities", [])
            if gi is not None:
                if not isinstance(gi, int) or gi < 0 or gi >= len(gt_ents):
                    errors.append(f"{ep}.gt_index={gi} out of range (GT has {len(gt_ents)} entities)")
            if not isinstance(eg.get("flag", False), bool):
                errors.append(f"{ep}.flag must be boolean")

        # Validate missed indices
        gt_locs = eval_input.get("ground_truth", {}).get("locations", [])
        gt_ents = eval_input.get("ground_truth", {}).get("entities", [])
        for mi in ev.get("missed_locations", []):
            if not isinstance(mi, int) or mi < 0 or mi >= len(gt_locs):
                errors.append(f"{prefix}.missed_locations contains {mi}, out of range")
        for mi in ev.get("missed_entities", []):
            if not isinstance(mi, int) or mi < 0 or mi >= len(gt_ents):
                errors.append(f"{prefix}.missed_entities contains {mi}, out of range")

        # Validate description score
        ds = ev.get("desc_score")
        if ds is not None and ds not in VALID_DESC_SCORES:
            errors.append(f"{prefix}.desc_score must be 0-4 or null, got {ds!r}")
        if ai == CLOUD_VISION_INDEX and ds is not None:
            errors.append(f"{prefix}.desc_score must be null for Google Cloud Vision")
        if not isinstance(ev.get("desc_reason", ""), str) and ev.get("desc_reason") is not None:
            errors.append(f"{prefix}.desc_reason must be a string or null")

    return errors


# ── Build logic ──────────────────────────────────────────────────────────────

def compute_desc_max_achievable(gt: dict) -> int:
    """Derive description max_achievable from GT max_specificity field."""
    ms = (gt.get("max_specificity") or "").lower()
    if "specific" in ms and "generic" not in ms:
        return 4
    return 3


def resolve_location_text(details: dict, source: str, index: int) -> str:
    """Get location name text from model output."""
    arr = details.get(source, [])
    if 0 <= index < len(arr):
        return arr[index].get("name", "")
    return ""


def resolve_entity_text(details: dict, index: int) -> tuple[str, str]:
    """Get (entity name, entity type) from model output."""
    arr = details.get("entities", [])
    if 0 <= index < len(arr):
        return arr[index].get("name", ""), arr[index].get("type", "")
    return "", ""


def build_evaluation(scores: dict, eval_input: dict) -> dict:
    """Build full evaluation JSON from compact scores + eval_input."""
    gt = eval_input.get("ground_truth", {})
    model_runs = eval_input.get("model_runs", [])
    gt_locs = gt.get("locations", [])
    gt_ents = gt.get("entities", [])

    desc_max = compute_desc_max_achievable(gt)

    human_review_items: list[dict] = []
    evaluations: list[dict] = []

    for ev in scores.get("evals", []):
        ri = ev["run_index"]
        ai = ev["approach_index"]
        run = model_runs[ri]
        approach_data = get_approach_by_canonical_index(run, ai)
        if approach_data is None:
            raise ValueError(f"Approach {APPROACH_NAMES[ai]!r} not found in run {ri}")
        details = approach_data.get("details", {})
        gps_mode = run.get("use_gps", False)
        approach_name = APPROACH_NAMES[ai]

        # ── Location claims ──
        location_claims: list[dict] = []
        for lg in ev.get("location_groups", []):
            src = lg["source"]
            indices = lg.get("model_indices", [])
            representative_idx = indices[0] if indices else None
            rep_text = resolve_location_text(details, src, representative_idx) if representative_idx is not None else ""
            all_texts = [resolve_location_text(details, src, mi) for mi in indices]
            gi = lg.get("gt_index")

            claim = {
                "source": src,
                "model_indices": indices,
                "representative_text": rep_text,
                "all_texts": all_texts,
                "reference_type": lg["ref_type"],
                "specificity": lg["specificity"],
                "correctness": float(lg["correctness"]),
                "correctness_reason": lg.get("reason", ""),
                "gt_location_index": gi,
                "gt_location_name": gt_locs[gi]["name"] if gi is not None and gi < len(gt_locs) else None,
                "possibly_true_not_in_gt": lg.get("flag", False),
            }
            location_claims.append(claim)

            if lg.get("flag", False):
                human_review_items.append({
                    "gps_mode": gps_mode,
                    "approach": approach_name,
                    "claim_type": "location",
                    "source": src,
                    "group_model_indices": indices,
                    "representative_text": rep_text,
                    "reason": lg.get("reason", ""),
                })

        # ── Entity claims ──
        entity_claims: list[dict] = []
        for eg in ev.get("entity_groups", []):
            indices = eg.get("model_indices", [])
            representative_idx = indices[0] if indices else None
            rep_name, rep_type = resolve_entity_text(details, representative_idx) if representative_idx is not None else ("", "")
            all_names = [resolve_entity_text(details, mi)[0] for mi in indices]
            gi = eg.get("gt_index")

            claim = {
                "model_indices": indices,
                "representative_text": rep_name,
                "all_texts": all_names,
                "category": rep_type,
                "specificity": eg["specificity"],
                "correctness": float(eg["correctness"]),
                "correctness_reason": eg.get("reason", ""),
                "gt_entity_index": gi,
                "gt_entity_name": gt_ents[gi]["name"] if gi is not None and gi < len(gt_ents) else None,
                "possibly_true_not_in_gt": eg.get("flag", False),
            }
            entity_claims.append(claim)

            if eg.get("flag", False):
                human_review_items.append({
                    "gps_mode": gps_mode,
                    "approach": approach_name,
                    "claim_type": "entity",
                    "group_model_indices": indices,
                    "representative_text": rep_name,
                    "reason": eg.get("reason", ""),
                })

        # ── False negatives ──
        missed_locs = [
            {"gt_index": mi, "gt_name": gt_locs[mi]["name"] if mi < len(gt_locs) else "?"}
            for mi in ev.get("missed_locations", [])
        ]
        missed_ents = [
            {"gt_index": mi, "gt_name": gt_ents[mi]["name"] if mi < len(gt_ents) else "?"}
            for mi in ev.get("missed_entities", [])
        ]

        # ── Description ──
        ds = ev.get("desc_score")
        desc_score = {
            "score": ds,
            "max_achievable": desc_max,
            "justification": ev.get("desc_reason") or "",
        }

        evaluations.append({
            "gps_mode": gps_mode,
            "approach": approach_name,
            "location_claims": location_claims,
            "entity_claims": entity_claims,
            "false_negatives": {
                "missed_locations": missed_locs,
                "missed_entities": missed_ents,
            },
            "description_score": desc_score,
        })

    output = {
        "image_id": eval_input["image_id"],
        "filename": eval_input["filename"],
        "ground_truth_summary": {
            "locations_count": len(gt_locs),
            "entities_count": len(gt_ents),
            "max_specificity": gt.get("max_specificity"),
            "difficulty": gt.get("difficulty"),
        },
        "max_entity_specificity": scores.get("max_entity_specificity"),
        "evaluator_notes": scores.get("evaluator_notes"),
        "human_review_items": human_review_items,
        "evaluations": evaluations,
    }
    return output


# ── Main ─────────────────────────────────────────────────────────────────────

def process_image(image_id: int, validate_only: bool = False) -> bool:
    """Process one image. Return True if successful."""
    scores_path = SCORES_DIR / f"scores_{image_id:03d}.json"
    input_path = INPUTS_DIR / f"eval_input_{image_id:03d}.json"
    output_path = OUTPUTS_DIR / f"eval_{image_id:03d}.json"

    if not scores_path.exists():
        print(f"  skip image {image_id}: no scores file", file=sys.stderr)
        return False
    if not input_path.exists():
        print(f"  ERROR image {image_id}: no eval_input file", file=sys.stderr)
        return False

    scores = json.loads(scores_path.read_text(encoding="utf-8"))
    eval_input = json.loads(input_path.read_text(encoding="utf-8"))

    errors = validate_scores(scores, eval_input)
    if errors:
        print(f"  VALIDATION ERRORS for image {image_id}:", file=sys.stderr)
        for e in errors:
            print(f"    {e}", file=sys.stderr)
        return False

    if validate_only:
        print(f"  image {image_id}: valid", file=sys.stderr)
        return True

    result = build_evaluation(scores, eval_input)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  image {image_id}: wrote {output_path.name}", file=sys.stderr)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Build evaluation JSON from compact scores")
    parser.add_argument("--image-id", type=int, help="Process a single image ID")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't write output")
    args = parser.parse_args()

    if args.image_id is not None:
        ok = process_image(args.image_id, args.validate_only)
        sys.exit(0 if ok else 1)

    # Process all scores files
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    scores_files = sorted(SCORES_DIR.glob("scores_*.json"))
    if not scores_files:
        print(f"No scores files in {SCORES_DIR}", file=sys.stderr)
        sys.exit(1)

    ok_count = 0
    fail_count = 0
    for sf in scores_files:
        # Extract image_id from filename
        try:
            stem = sf.stem  # e.g. "scores_016"
            img_id = int(stem.split("_")[1])
        except (IndexError, ValueError):
            print(f"  skip {sf.name}: cannot parse image_id from filename", file=sys.stderr)
            fail_count += 1
            continue
        if process_image(img_id, args.validate_only):
            ok_count += 1
        else:
            fail_count += 1

    print(f"\nDone: {ok_count} succeeded, {fail_count} failed", file=sys.stderr)
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
