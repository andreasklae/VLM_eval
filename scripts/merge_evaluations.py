#!/usr/bin/env python3
"""
Merge per-image evaluation JSON files into one dataset.

Reads all eval_*.json from results/.eval_work/outputs/ (produced by
build_evaluation.py), validates structure and scoring values, then writes
results/evaluation_dataset.json and results/evaluation_summary.json.
Per-image files are left in place as backups.

Usage:
    python scripts/merge_evaluations.py
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
OUTPUTS_DIR = ROOT / "results" / ".eval_work" / "outputs"
MERGED_PATH = ROOT / "results" / "evaluation_dataset.json"
SUMMARY_PATH = ROOT / "results" / "evaluation_summary.json"

APPROACH_NAMES = [
    "GPT Vision Direct (strong)",
    "GPT Vision Direct (fast)",
    "GPT Vision + Search (strong)",
    "GPT Vision + Search (fast)",
    "Gemini Vision (strong)",
    "Gemini Vision (fast)",
    "Google Cloud Vision",
]
APPROACH_SET = frozenset(APPROACH_NAMES)
CORRECTNESS_VALUES = frozenset({-1.0, -0.5, 0.0, 0.5, 1.0})
VALID_SPECIFICITY = frozenset({1, 2, 3, 4, 5})
DESCRIPTION_SCORE_VALUES = frozenset({0, 1, 2, 3, 4})
REFERENCE_TYPES = frozenset({"photographer_position", "depicted_subject", "ambiguous_or_unspecified"})
VALID_SOURCES = frozenset({"photographer_location", "subject_location"})


def validate_evaluation(data: dict, path: Path) -> list[str]:
    """Validate one eval_*.json (output of build_evaluation.py)."""
    errors: list[str] = []

    # Top-level fields
    if not isinstance(data.get("image_id"), int):
        errors.append("missing or invalid image_id")
    if not isinstance(data.get("filename"), str):
        errors.append("missing or invalid filename")
    mes = data.get("max_entity_specificity")
    if mes is not None and mes not in VALID_SPECIFICITY:
        errors.append(f"max_entity_specificity must be 1-5 or null, got {mes!r}")

    evals = data.get("evaluations", [])
    # Don't require exactly 14 — images with missing runs may have fewer
    for i, ev in enumerate(evals):
        if not isinstance(ev.get("gps_mode"), bool):
            errors.append(f"evaluations[{i}].gps_mode must be boolean")
        ap = ev.get("approach")
        if ap not in APPROACH_SET:
            errors.append(f"evaluations[{i}].approach invalid: {ap!r}")

        # Location claims
        for j, loc in enumerate(ev.get("location_claims", [])):
            lp = f"evaluations[{i}].location_claims[{j}]"
            s = loc.get("specificity")
            if s is not None and s not in VALID_SPECIFICITY:
                errors.append(f"{lp}.specificity must be 1-5, got {s!r}")
            c = loc.get("correctness")
            if c is not None and c not in CORRECTNESS_VALUES:
                errors.append(f"{lp}.correctness invalid: {c!r}")
            rt = loc.get("reference_type")
            if rt is not None and rt not in REFERENCE_TYPES:
                errors.append(f"{lp}.reference_type invalid: {rt!r}")
            src = loc.get("source")
            if src is not None and src not in VALID_SOURCES:
                errors.append(f"{lp}.source invalid: {src!r}")

        # Entity claims
        for j, ent in enumerate(ev.get("entity_claims", [])):
            ep = f"evaluations[{i}].entity_claims[{j}]"
            s = ent.get("specificity")
            if s is not None and s not in VALID_SPECIFICITY:
                errors.append(f"{ep}.specificity must be 1-5, got {s!r}")
            c = ent.get("correctness")
            if c is not None and c not in CORRECTNESS_VALUES:
                errors.append(f"{ep}.correctness invalid: {c!r}")

        # Description score
        ds = ev.get("description_score")
        if ds is not None:
            score = ds.get("score")
            if score is not None and score not in DESCRIPTION_SCORE_VALUES:
                errors.append(f"evaluations[{i}].description_score.score must be 0-4 or null, got {score!r}")

        # False negatives
        fn = ev.get("false_negatives", {})
        for item in fn.get("missed_locations", []):
            if not isinstance(item.get("gt_index"), int) or "gt_name" not in item:
                errors.append(f"evaluations[{i}].false_negatives.missed_locations entry missing gt_index/gt_name")
        for item in fn.get("missed_entities", []):
            if not isinstance(item.get("gt_index"), int) or "gt_name" not in item:
                errors.append(f"evaluations[{i}].false_negatives.missed_entities entry missing gt_index/gt_name")

    return errors


def main() -> None:
    if not OUTPUTS_DIR.exists():
        print(f"Error: {OUTPUTS_DIR} not found. Run build_evaluation.py first.", file=sys.stderr)
        sys.exit(1)

    paths = sorted(OUTPUTS_DIR.glob("eval_*.json"))
    if not paths:
        print(f"Error: no eval_*.json files in {OUTPUTS_DIR}", file=sys.stderr)
        sys.exit(1)

    images: list[dict] = []
    all_errors: list[str] = []
    for p in paths:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            all_errors.append(f"{p.name}: load error — {e}")
            continue
        errs = validate_evaluation(data, p)
        if errs:
            all_errors.append(f"{p.name}: " + "; ".join(errs))
        else:
            images.append(data)

    if all_errors:
        print("Validation errors:", file=sys.stderr)
        for e in all_errors:
            print(f"  {e}", file=sys.stderr)
        if not images:
            sys.exit(1)

    images.sort(key=lambda x: x.get("image_id", 0))
    total_evals = sum(len(img.get("evaluations", [])) for img in images)
    total_review = sum(len(img.get("human_review_items", [])) for img in images)

    # Per-approach statistics
    approach_stats: dict[str, Counter] = {name: Counter() for name in APPROACH_NAMES}
    for img in images:
        for ev in img.get("evaluations", []):
            ap = ev.get("approach", "")
            if ap in approach_stats:
                approach_stats[ap]["count"] += 1
                ds = ev.get("description_score", {})
                if ds and ds.get("score") is not None:
                    approach_stats[ap]["desc_score_sum"] += ds["score"]
                    approach_stats[ap]["desc_score_count"] += 1

    merged = {
        "metadata": {
            "created": datetime.now().isoformat()[:10],
            "total_images": len(images),
            "total_evaluations": total_evals,
            "total_human_review_items": total_review,
            "approaches": APPROACH_NAMES,
            "scoring": {
                "specificity_range": "1-5",
                "correctness_values": sorted(CORRECTNESS_VALUES),
                "description_score_range": "0-4",
            },
        },
        "images": images,
    }

    MERGED_PATH.parent.mkdir(parents=True, exist_ok=True)
    MERGED_PATH.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {MERGED_PATH} ({len(images)} images, {total_evals} evaluations)", file=sys.stderr)

    summary = {
        "total_images": len(images),
        "total_evaluations": total_evals,
        "total_human_review_items": total_review,
        "validation_errors": len(all_errors),
        "files_merged": len(paths),
        "per_approach": {
            name: {
                "evaluations": stats["count"],
                "avg_desc_score": round(stats["desc_score_sum"] / stats["desc_score_count"], 2) if stats["desc_score_count"] > 0 else None,
            }
            for name, stats in approach_stats.items()
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {SUMMARY_PATH}", file=sys.stderr)

    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
