#!/usr/bin/env python3
"""
Batch testing script for image recognition.

Calls the image recognition API for all images in test_images/ directory
and saves results to JSON and Markdown files.

Usage:
    python batch_test.py
    python batch_test.py --server-url http://localhost:8000
    python batch_test.py --output-dir results/
"""

import argparse
import asyncio
import json
import mimetypes
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

# Add backend to path for metadata extraction
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "image_recognition"))
try:
    from metadata import extract_metadata
    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False
    print("Warning: Could not import metadata module. GPS detection disabled.", file=sys.stderr)


def has_gps_metadata(image_path: Path) -> bool:
    """Check if image has GPS coordinates in EXIF metadata."""
    if not METADATA_AVAILABLE:
        return True  # Assume yes if we can't check (conservative)

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        metadata = extract_metadata(image_data)
        return metadata.gps_latitude is not None and metadata.gps_longitude is not None
    except Exception:
        return True  # Assume yes on error (conservative)


# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".heif", ".JPG", ".JPEG", ".PNG", ".HEIC", ".HEIF"}


def find_test_images(test_dir: Path) -> list[Path]:
    """Find all image files in the test directory."""
    if not test_dir.exists():
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(test_dir.glob(f"*{ext}"))

    return sorted(images)


def image_id_from_path(path: Path) -> int | None:
    """Extract numeric id from image path stem (e.g. 100.jpg -> 100). Returns None if not a number."""
    try:
        return int(path.stem)
    except ValueError:
        return None


def filter_images_by_id_range(images: list[Path], id_min: int | None, id_max: int | None) -> list[Path]:
    """Filter images to those whose stem is a number in [id_min, id_max] (inclusive)."""
    if id_min is None and id_max is None:
        return images
    out = []
    for p in images:
        n = image_id_from_path(p)
        if n is None:
            continue
        if id_min is not None and n < id_min:
            continue
        if id_max is not None and n > id_max:
            continue
        out.append(p)
    return sorted(out)


def sample_images(images: list[Path], limit: int | None, random_sample: bool = False) -> list[Path]:
    """Optionally limit to first N or random N images."""
    if limit is None or limit <= 0 or len(images) <= limit:
        return images
    if random_sample:
        return random.sample(images, limit)
    return images[:limit]


async def process_image(
    client: httpx.AsyncClient,
    image_path: Path,
    server_url: str,
    approaches: str | None = None,
    use_gps: bool = True,
) -> dict[str, Any]:
    """Process a single image by calling the API."""
    start_time = datetime.now()

    # Prepare request
    url = f"{server_url}/recognize"
    params = {"use_gps": str(use_gps).lower()}
    if approaches:
        params["approaches"] = approaches

    try:
        # Read image file and prepare for upload
        with open(image_path, "rb") as f:
            image_data = f.read()
            # Detect MIME type from filename (important for HEIC support)
            mime_type, _ = mimetypes.guess_type(image_path.name)
            if not mime_type or not mime_type.startswith("image/"):
                # Handle HEIC/HEIF explicitly as mimetypes may not recognize them
                ext_lower = image_path.suffix.lower()
                if ext_lower in {'.heic', '.heif'}:
                    mime_type = "image/heic"
                else:
                    mime_type = "image/jpeg"  # Default fallback
            files = {"image": (image_path.name, image_data, mime_type)}

            # Make API request (8 approaches in parallel on server can take 2–5+ minutes)
            response = await client.post(url, files=files, params=params)
            response.raise_for_status()
            result = response.json()

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Add image path, GPS flag, and request-level success to result
        result["image_path"] = str(image_path)
        result["use_gps"] = use_gps
        result["success"] = True  # request succeeded (individual approaches may still have failed)

        # Log GPS/metadata if present
        metadata_info = ""
        if use_gps and result.get("metadata"):
            metadata = result["metadata"]
            metadata_parts = []
            if metadata.get("gps_latitude") is not None and metadata.get("gps_longitude") is not None:
                metadata_parts.append(f"GPS: {metadata['gps_latitude']:.4f}, {metadata['gps_longitude']:.4f}")
            if metadata.get("datetime_original"):
                metadata_parts.append(f"Date: {metadata['datetime_original']}")
            if metadata.get("camera_make") or metadata.get("camera_model"):
                camera = f"{metadata.get('camera_make', '')} {metadata.get('camera_model', '')}".strip()
                metadata_parts.append(f"Camera: {camera}")
            if metadata_parts:
                metadata_info = f" [{', '.join(metadata_parts)}]"
            else:
                metadata_info = " [no metadata found]"
        elif use_gps:
            metadata_info = " [no GPS/metadata found]"
        # Per-image summary
        print(
            f"✓ {image_path.name} (total={processing_time:.1f}s, gps={'on' if use_gps else 'off'}{metadata_info})",
            file=sys.stderr,
        )
        # Per-approach summary (after the server has finished running all approaches)
        for app in result.get("approaches", []):
            approach_name = app.get("approach", "unknown")
            success = app.get("success", False)
            identified = app.get("identified")
            error_msg = app.get("error")
            details = app.get("details") or {}
            t_ms = details.get("processing_time_ms")
            time_str = f"{t_ms/1000:.1f}s" if isinstance(t_ms, (int, float)) else "n/a"
            status = "ok" if success else "FAIL"
            ident_str = identified if identified is not None else "-"
            err_str = error_msg if error_msg else ""
            print(
                f"    - {approach_name}: {status}, t={time_str}, id={ident_str}{(' — ' + err_str) if err_str else ''}",
                file=sys.stderr,
            )
        return result

    except httpx.HTTPStatusError as e:
        err_msg = f"HTTP {e.response.status_code}: {(e.response.text or '').strip() or '(no body)'}"
        print(f"✗ {err_msg}", file=sys.stderr)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        return {
            "image_filename": image_path.name,
            "image_path": str(image_path),
            "processing_time_seconds": processing_time,
            "timestamp": start_time.isoformat(),
            "use_gps": use_gps,
            "success": False,
            "request_error": err_msg,
            "approaches": [
                {
                    "approach": "API Error",
                    "identified": None,
                    "confidence": None,
                    "success": False,
                    "error": err_msg,
                    "details": {},
                }
            ],
        }
    except Exception as e:
        err_msg = str(e).strip() or f"{type(e).__name__}"
        print(f"✗ Error: {err_msg}", file=sys.stderr)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        return {
            "image_filename": image_path.name,
            "image_path": str(image_path),
            "processing_time_seconds": processing_time,
            "timestamp": start_time.isoformat(),
            "use_gps": use_gps,
            "success": False,
            "request_error": err_msg,
            "approaches": [
                {
                    "approach": "Client Error",
                    "identified": None,
                    "confidence": None,
                    "success": False,
                    "error": err_msg,
                    "details": {},
                }
            ],
        }


async def batch_test(
    test_dir: Path,
    output_dir: Path,
    server_url: str,
    approaches: str | None = None,
    limit: int | None = None,
    id_min: int | None = None,
    id_max: int | None = None,
    both_metadata: bool = False,
    parallel: bool = False,
) -> None:
    """Run batch testing on all images in test directory."""
    # Find all test images
    images = find_test_images(test_dir)
    if id_min is not None or id_max is not None:
        images = filter_images_by_id_range(images, id_min, id_max)
        print(f"Filtered to id range [{id_min or 'any'}, {id_max or 'any'}]: {len(images)} image(s)", file=sys.stderr)
    if limit is not None and limit > 0 and len(images) > limit:
        # Random sample when using id range (e.g. "3 random between 100-200"), else first N
        random_sample = id_min is not None or id_max is not None
        images = sample_images(images, limit, random_sample=random_sample)
        print(f"Using {len(images)} image(s)" + (" (random sample)" if random_sample else " (first N)"), file=sys.stderr)
    if not images:
        print(f"No images found in {test_dir}", file=sys.stderr)
        return

    # Establish test run timestamp and output paths up front
    test_start = datetime.now()
    date_str = test_start.strftime("%Y-%m-%d")
    date_readable = test_start.strftime("%B %d, %Y")
    output_dir.mkdir(parents=True, exist_ok=True)
    # Streaming JSONL file (one result per line, written incrementally)
    jsonl_path = output_dir / f"batch_test_results_{date_str}.jsonl"
    # Truncate any existing file for this date
    with open(jsonl_path, "w", encoding="utf-8") as jf:
        jf.write("")  # empty file, we'll append as we go

    print(f"Found {len(images)} image(s) in {test_dir}", file=sys.stderr)
    print(f"Server URL: {server_url}", file=sys.stderr)

    # Check server health
    # Long timeout: server runs 8 approaches per request; each image can take 2–5+ minutes
    timeout = httpx.Timeout(60.0, read=600.0)  # 60s connect, 10 min read
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            health_response = await client.get(f"{server_url}/health")
            health_response.raise_for_status()
            print("✓ Server is healthy", file=sys.stderr)
        except Exception as e:
            print(f"⚠ Warning: Could not reach server at {server_url}: {e}", file=sys.stderr)
            print("  Make sure the server is running before proceeding.", file=sys.stderr)

        # Get available approaches from server
        try:
            approaches_response = await client.get(f"{server_url}/approaches")
            approaches_response.raise_for_status()
            available_approaches = approaches_response.json()
            approach_names = [a["name"] for a in available_approaches if a["available"]]
            print(f"Available approaches: {', '.join(approach_names)}", file=sys.stderr)
        except Exception as e:
            print(f"⚠ Warning: Could not fetch approaches: {e}", file=sys.stderr)
            approach_names = []

        print("", file=sys.stderr)

        # Build list of (image_path, use_gps) tasks
        if both_metadata:
            tasks = []
            for image_path in images:
                tasks.append((image_path, True))
                tasks.append((image_path, False))
            images_with_gps = images  # for report; we run both for all
            images_without_gps = []
            print(f"Running {len(tasks)} tests (each image with and without GPS)...", file=sys.stderr)
        else:
            # Pre-scan for GPS metadata
            images_with_gps = []
            images_without_gps = []
            for image_path in images:
                if has_gps_metadata(image_path):
                    images_with_gps.append(image_path)
                else:
                    images_without_gps.append(image_path)
            print(f"  Images with GPS: {len(images_with_gps)}", file=sys.stderr)
            print(f"  Images without GPS: {len(images_without_gps)} (skipping GPS=on test)", file=sys.stderr)
            tasks = []
            for image_path in images:
                if image_path in images_with_gps:
                    tasks.append((image_path, True))
                tasks.append((image_path, False))

        print("", file=sys.stderr)

        if parallel and len(tasks) > 1:
            print(f"Running {len(tasks)} requests in parallel...", file=sys.stderr)
            results = await asyncio.gather(
                *[
                    process_image(client, path, server_url, approaches, use_md)
                    for path, use_md in tasks
                ]
            )
            all_results = list(results)
            for (path, use_md), result in zip(tasks, all_results):
                print(f"  ✓ {path.name} (gps={'on' if use_md else 'off'})", file=sys.stderr)
                # Append each result incrementally to JSONL (formatted for readability)
                with open(jsonl_path, "a", encoding="utf-8") as jf:
                    json.dump(result, jf, indent=2, ensure_ascii=False)
                    jf.write("\n")
        else:
            all_results = []
            for i, (image_path, use_gps_flag) in enumerate(tasks, 1):
                print(f"[{i}/{len(tasks)}] {image_path.name} (gps={'on' if use_gps_flag else 'off'})... ", end="", file=sys.stderr)
                result = await process_image(client, image_path, server_url, approaches, use_gps_flag)
                all_results.append(result)
                # Append each result incrementally to JSONL (formatted for readability)
                with open(jsonl_path, "a", encoding="utf-8") as jf:
                    json.dump(result, jf, indent=2, ensure_ascii=False)
                    jf.write("\n")

    gps_testing_desc = (
        "Each image tested both with and without GPS (--both-metadata)."
        if both_metadata
        else "Images with GPS tested twice (with/without GPS). Images without GPS tested once (gps=off only)."
    )

    # Build failed_attempts: request-level failures and per-approach failures
    failed_attempts: list[dict[str, Any]] = []
    for result in all_results:
        image_path_str = result.get("image_path", "")
        use_gps_flag = result.get("use_gps", True)
        # Request-level failure (no successful API response)
        if result.get("success") is False and result.get("request_error"):
            failed_attempts.append({
                "image_path": image_path_str,
                "use_gps": use_gps_flag,
                "failure_type": "request",
                "approach": None,
                "error": result.get("request_error", "Unknown error"),
            })
            continue
        # Per-approach failures within a successful request
        for app in result.get("approaches", []):
            if app.get("success") is False and app.get("error"):
                failed_attempts.append({
                    "image_path": image_path_str,
                    "use_gps": use_gps_flag,
                    "failure_type": "approach",
                    "approach": app.get("approach"),
                    "error": app.get("error", "Unknown error"),
                })

    # Create output data structure
    output_data = {
        "test_run": {
            "date": date_str,
            "date_readable": date_readable,
            "timestamp": test_start.isoformat(),
            "server_url": server_url,
            "test_directory": str(test_dir),
            "total_images": len(images),
            "images_with_gps": len(images_with_gps),
            "images_without_gps": len(images_without_gps),
            "total_tests": len(all_results),
            "failed_attempts_count": len(failed_attempts),
            "approaches_used": approach_names if approach_names else "all",
            "gps_testing": gps_testing_desc,
        },
        "failed_attempts": failed_attempts,
        "results": all_results,
    }

    # Save JSON with date in filename
    output_dir.mkdir(parents=True, exist_ok=True)
    json_filename = f"batch_test_results_{date_str}.json"
    json_path = output_dir / json_filename
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved JSON results to: {json_path}", file=sys.stderr)

    # Print summary
    print("\n" + "=" * 60, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Test Date: {date_readable}", file=sys.stderr)
    print(f"Server URL: {server_url}", file=sys.stderr)
    print(f"Total images: {len(images)}", file=sys.stderr)
    print(f"  - With GPS metadata: {len(images_with_gps)} (tested with and without metadata)", file=sys.stderr)
    print(f"  - Without GPS metadata: {len(images_without_gps)} (tested without metadata only)", file=sys.stderr)
    print(f"Total tests: {len(all_results)}", file=sys.stderr)
    print(f"Failed attempts (request or approach): {len(failed_attempts)}", file=sys.stderr)
    if failed_attempts:
        for fa in failed_attempts[:10]:
            print(f"  - {fa.get('image_path', '')} (gps={fa.get('use_gps')}) {fa.get('failure_type')}: {fa.get('approach') or 'request'} — {fa.get('error', '')[:80]}", file=sys.stderr)
        if len(failed_attempts) > 10:
            print(f"  ... and {len(failed_attempts) - 10} more (see failed_attempts in JSON)", file=sys.stderr)

    # Count successes per approach, split by GPS usage
    approach_stats = {}
    gps_stats = {"with_gps": {"success": 0, "failed": 0, "total": 0}, "without_gps": {"success": 0, "failed": 0, "total": 0}}
    
    for result in all_results:
        use_gps_flag = result.get("use_gps", True)
        gps_key = "with_gps" if use_gps_flag else "without_gps"
        
        for approach_result in result["approaches"]:
            approach_name = approach_result["approach"]
            if approach_name not in approach_stats:
                approach_stats[approach_name] = {
                    "with_gps": {"success": 0, "failed": 0, "total": 0},
                    "without_gps": {"success": 0, "failed": 0, "total": 0},
                }
            
            approach_stats[approach_name][gps_key]["total"] += 1
            gps_stats[gps_key]["total"] += 1
            
            if approach_result["success"]:
                approach_stats[approach_name][gps_key]["success"] += 1
                gps_stats[gps_key]["success"] += 1
            else:
                approach_stats[approach_name][gps_key]["failed"] += 1
                gps_stats[gps_key]["failed"] += 1

    print("\nOverall statistics by GPS usage:", file=sys.stderr)
    for key, stats in gps_stats.items():
        success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        label = "With GPS" if key == "with_gps" else "Without GPS"
        print(
            f"  {label}: {stats['success']}/{stats['total']} succeeded ({success_rate:.1f}%)",
            file=sys.stderr,
        )
    
    print("\nApproach statistics (by GPS usage):", file=sys.stderr)
    for approach_name, stats in sorted(approach_stats.items()):
        print(f"  {approach_name}:", file=sys.stderr)
        for key in ["with_gps", "without_gps"]:
            label = "    With GPS" if key == "with_gps" else "    Without GPS"
            s = stats.get(key, {"success": 0, "total": 0})
            success_rate = (s["success"] / s["total"] * 100) if s["total"] > 0 else 0
            print(
                f"      {label}: {s['success']}/{s['total']} succeeded ({success_rate:.1f}%)",
                file=sys.stderr,
            )


def main():
    """Main entry point."""
    import asyncio

    script_dir = Path(__file__).parent
    default_test_dir = script_dir / "test_images"
    default_output_dir = script_dir / "results"
    default_server_url = "http://localhost:8000"

    parser = argparse.ArgumentParser(
        description="Run batch image recognition tests via API on all images in test_images/ directory"
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=default_test_dir,
        help=f"Directory containing test images (default: {default_test_dir})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir,
        help=f"Directory to save results (default: {default_output_dir})",
    )
    parser.add_argument(
        "--server-url",
        type=str,
        default=default_server_url,
        help=f"URL of the image recognition API server (default: {default_server_url})",
    )
    parser.add_argument(
        "--approaches",
        type=str,
        default=None,
        help="Comma-separated list of approach names to use (default: all available)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Run only on the first N images (default: all). With --id-min/--id-max, randomly sample N.",
    )
    parser.add_argument(
        "--id-min",
        type=int,
        default=None,
        metavar="N",
        help="Only include images whose filename stem (e.g. 100 from 100.jpg) is >= N",
    )
    parser.add_argument(
        "--id-max",
        type=int,
        default=None,
        metavar="N",
        help="Only include images whose filename stem is <= N",
    )
    parser.add_argument(
        "--both-metadata",
        action="store_true",
        help="Run each image both with and without metadata (ignore GPS check)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run all API requests in parallel (faster, higher load)",
    )

    args = parser.parse_args()

    asyncio.run(
        batch_test(
            args.test_dir,
            args.output_dir,
            args.server_url,
            args.approaches,
            limit=args.limit,
            id_min=args.id_min,
            id_max=args.id_max,
            both_metadata=args.both_metadata,
            parallel=args.parallel,
        )
    )


if __name__ == "__main__":
    main()
