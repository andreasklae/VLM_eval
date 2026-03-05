#!/usr/bin/env python3
"""
Single image testing script for image recognition.

Tests a single image with the image recognition API, testing both with and without metadata.
Saves results to JSON and optionally Markdown files.

Usage:
    python test_single.py path/to/image.jpg
    python test_single.py path/to/image.jpg --server-url http://localhost:8000
    python test_single.py path/to/image.jpg --output-dir results/
    python test_single.py path/to/image.jpg --json-only
"""

import argparse
import json
import mimetypes
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


async def process_image(
    client: httpx.AsyncClient,
    image_path: Path,
    server_url: str,
    approaches: str | None = None,
    use_metadata: bool = True,
) -> dict[str, Any]:
    """Process a single image by calling the API."""
    start_time = datetime.now()

    # Prepare request
    url = f"{server_url}/recognize"
    params = {"use_metadata": str(use_metadata).lower()}
    if approaches:
        params["approaches"] = approaches

    try:
        # Read image file and prepare for upload
        with open(image_path, "rb") as f:
            image_data = f.read()
            # Detect MIME type from filename (important for HEIC support)
            mime_type, _ = mimetypes.guess_type(image_path.name)
            if not mime_type or not mime_type.startswith("image/"):
                mime_type = "image/jpeg"  # Default fallback
            files = {"image": (image_path.name, image_data, mime_type)}

            # Make API request
            response = await client.post(url, files=files, params=params, timeout=300.0)
            response.raise_for_status()
            result = response.json()

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Add image path and metadata flag to result
        result["image_path"] = str(image_path)
        result["use_metadata"] = use_metadata

        # Log metadata if present
        metadata_info = ""
        if use_metadata and result.get("metadata"):
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
        elif use_metadata:
            metadata_info = " [no metadata found]"

        print(f"✓ ({processing_time:.1f}s, metadata={'on' if use_metadata else 'off'}{metadata_info})", file=sys.stderr)
        return result

    except httpx.HTTPStatusError as e:
        print(f"✗ HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        return {
            "image_filename": image_path.name,
            "image_path": str(image_path),
            "processing_time_seconds": processing_time,
            "timestamp": start_time.isoformat(),
            "use_metadata": use_metadata,
            "approaches": [
                {
                    "approach": "API Error",
                    "identified": None,
                    "confidence": None,
                    "success": False,
                    "error": f"HTTP {e.response.status_code}: {e.response.text}",
                    "details": {},
                }
            ],
        }
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        return {
            "image_filename": image_path.name,
            "image_path": str(image_path),
            "processing_time_seconds": processing_time,
            "timestamp": start_time.isoformat(),
            "use_metadata": use_metadata,
            "approaches": [
                {
                    "approach": "Client Error",
                    "identified": None,
                    "confidence": None,
                    "success": False,
                    "error": str(e),
                    "details": {},
                }
            ],
        }


async def test_single_image(
    image_path: Path,
    output_dir: Path,
    server_url: str,
    approaches: str | None = None,
    json_only: bool = False,
) -> None:
    """Test a single image with and without metadata."""
    if not image_path.exists():
        print(f"Error: Image not found: {image_path}", file=sys.stderr)
        return

    print(f"Testing image: {image_path.name}", file=sys.stderr)
    print(f"Server URL: {server_url}", file=sys.stderr)

    # Check server health
    async with httpx.AsyncClient(timeout=10.0) as client:
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

        # Process image - test with and without metadata
        all_results = []
        
        # Test with metadata
        print(f"[1/2] {image_path.name} (metadata=on)... ", end="", file=sys.stderr)
        result_with_metadata = await process_image(client, image_path, server_url, approaches, use_metadata=True)
        all_results.append(result_with_metadata)

        # Test without metadata
        print(f"[2/2] {image_path.name} (metadata=off)... ", end="", file=sys.stderr)
        result_without_metadata = await process_image(client, image_path, server_url, approaches, use_metadata=False)
        all_results.append(result_without_metadata)

    # Get test date
    test_date = datetime.now()
    date_str = test_date.strftime("%Y-%m-%d")
    time_str = test_date.strftime("%H%M%S")
    date_readable = test_date.strftime("%B %d, %Y")

    # Create output data structure
    output_data = {
        "test_run": {
            "date": date_str,
            "date_readable": date_readable,
            "timestamp": test_date.isoformat(),
            "server_url": server_url,
            "image_path": str(image_path),
            "image_filename": image_path.name,
            "total_tests": len(all_results),
            "approaches_used": approach_names if approach_names else "all",
            "metadata_testing": "Image tested with metadata=True and metadata=False",
        },
        "results": all_results,
    }

    # Save JSON with date and time in filename
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = image_path.stem.replace(" ", "_")
    json_filename = f"test_{safe_filename}_{date_str}_{time_str}.json"
    json_path = output_dir / json_filename
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved JSON results to: {json_path}", file=sys.stderr)

    # Save Markdown report (unless json_only)
    if not json_only:
        md_filename = f"test_{safe_filename}_{date_str}_{time_str}.md"
        md_path = output_dir / md_filename
        markdown = generate_markdown_report(output_data)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"✓ Saved Markdown report to: {md_path}", file=sys.stderr)

    # Print summary
    print("\n" + "=" * 60, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Image: {image_path.name}", file=sys.stderr)
    print(f"Test Date: {date_readable}", file=sys.stderr)
    print(f"Server URL: {server_url}", file=sys.stderr)
    print(f"Total tests: {len(all_results)} (with and without metadata)", file=sys.stderr)

    # Count successes per approach, split by metadata usage
    approach_stats = {}
    metadata_stats = {"with_metadata": {"success": 0, "failed": 0, "total": 0}, "without_metadata": {"success": 0, "failed": 0, "total": 0}}

    for result in all_results:
        use_metadata = result.get("use_metadata", True)
        metadata_key = "with_metadata" if use_metadata else "without_metadata"

        for approach_result in result["approaches"]:
            approach_name = approach_result["approach"]
            if approach_name not in approach_stats:
                approach_stats[approach_name] = {
                    "with_metadata": {"success": 0, "failed": 0, "total": 0},
                    "without_metadata": {"success": 0, "failed": 0, "total": 0},
                }

            approach_stats[approach_name][metadata_key]["total"] += 1
            metadata_stats[metadata_key]["total"] += 1

            if approach_result["success"]:
                approach_stats[approach_name][metadata_key]["success"] += 1
                metadata_stats[metadata_key]["success"] += 1
            else:
                approach_stats[approach_name][metadata_key]["failed"] += 1
                metadata_stats[metadata_key]["failed"] += 1

    print("\nOverall statistics by metadata usage:", file=sys.stderr)
    for key, stats in metadata_stats.items():
        success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        label = "With metadata" if key == "with_metadata" else "Without metadata"
        print(
            f"  {label}: {stats['success']}/{stats['total']} succeeded ({success_rate:.1f}%)",
            file=sys.stderr,
        )

    print("\nApproach statistics (by metadata usage):", file=sys.stderr)
    for approach_name, stats in sorted(approach_stats.items()):
        print(f"  {approach_name}:", file=sys.stderr)
        for key in ["with_metadata", "without_metadata"]:
            label = "    With metadata" if key == "with_metadata" else "    Without metadata"
            s = stats[key]
            success_rate = (s["success"] / s["total"] * 100) if s["total"] > 0 else 0
            print(
                f"      {label}: {s['success']}/{s['total']} succeeded ({success_rate:.1f}%)",
                file=sys.stderr,
            )


def generate_markdown_report(data: dict[str, Any]) -> str:
    """Generate a human-readable Markdown report from test results."""
    lines = []
    lines.append("# Single Image Recognition Test Results")
    lines.append("")
    lines.append(f"**Test Date:** {data['test_run']['date_readable']} ({data['test_run']['date']})")
    lines.append(f"**Test Run Timestamp:** {data['test_run']['timestamp']}")
    lines.append(f"**Server URL:** {data['test_run']['server_url']}")
    lines.append(f"**Image:** `{data['test_run']['image_path']}`")
    lines.append(f"**Total Tests:** {data['test_run'].get('total_tests', len(data['results']))} (with and without metadata)")
    approaches_used = data['test_run']['approaches_used']
    if isinstance(approaches_used, list):
        lines.append(f"**Approaches Used:** {', '.join(approaches_used)}")
    else:
        lines.append(f"**Approaches Used:** {approaches_used}")
    lines.append(f"**Metadata Testing:** {data['test_run'].get('metadata_testing', 'N/A')}")
    lines.append("")

    # Add image preview
    image_path = data['test_run']['image_path']
    lines.append("## Test Image")
    lines.append("")
    lines.append(f'<img src="{image_path}" alt="Test image" style="max-width: 600px; max-height: 400px;">')
    lines.append("")
    lines.append("---")
    lines.append("")

    # Show both metadata scenarios
    for result in data["results"]:
        use_metadata = result.get("use_metadata", True)
        metadata_label = "**WITH METADATA**" if use_metadata else "**WITHOUT METADATA**"
        lines.append(f"## {metadata_label}")
        lines.append("")
        lines.append(f"**Processing Time:** {result['processing_time_seconds']:.2f} seconds")
        lines.append(f"**Timestamp:** {result['timestamp']}")

        # Show metadata if present
        if use_metadata:
            if result.get("metadata"):
                metadata = result["metadata"]
                lines.append("")
                lines.append("**Extracted Metadata:**")
                if metadata.get("gps_latitude") is not None and metadata.get("gps_longitude") is not None:
                    lines.append(f"- GPS Coordinates: {metadata['gps_latitude']:.6f}, {metadata['gps_longitude']:.6f}")
                    if metadata.get("gps_altitude") is not None:
                        lines.append(f"- GPS Altitude: {metadata['gps_altitude']:.2f} meters")
                # Show reverse-geocoded location
                if metadata.get("location"):
                    loc = metadata["location"]
                    if loc.get("formatted_address"):
                        lines.append(f"- **Location:** {loc['formatted_address']}")
                    location_parts = []
                    if loc.get("city"):
                        location_parts.append(f"City: {loc['city']}")
                    if loc.get("county"):
                        location_parts.append(f"County: {loc['county']}")
                    if loc.get("country"):
                        location_parts.append(f"Country: {loc['country']}")
                    if location_parts:
                        lines.append(f"  - {', '.join(location_parts)}")
                if metadata.get("datetime_original"):
                    lines.append(f"- Photo Taken: {metadata['datetime_original']}")
                if metadata.get("camera_make") or metadata.get("camera_model"):
                    camera = f"{metadata.get('camera_make', '')} {metadata.get('camera_model', '')}".strip()
                    lines.append(f"- Camera: {camera}")
                if metadata.get("orientation"):
                    lines.append(f"- Orientation: {metadata['orientation']}")
            else:
                lines.append("")
                lines.append("**Extracted Metadata:** None (no EXIF data found in image)")

        lines.append("")

        for approach_result in result["approaches"]:
            lines.append(f"### {approach_result['approach']}")
            lines.append("")

            if approach_result["error"]:
                lines.append(f"**Status:** ❌ Error")
                lines.append(f"**Error:** {approach_result['error']}")
            elif approach_result["success"]:
                lines.append(f"**Status:** ✅ Success")
                if approach_result["identified"]:
                    lines.append(f"**Identified:** {approach_result['identified']}")
                if approach_result["confidence"] is not None:
                    lines.append(f"**Confidence:** {approach_result['confidence']:.1%}")
            else:
                lines.append(f"**Status:** ⚠️ No identification")
                if approach_result["identified"]:
                    lines.append(f"**Identified:** {approach_result['identified']}")
            
            # Show per-approach processing time if available
            if approach_result.get("details") and isinstance(approach_result["details"], dict):
                processing_time_ms = approach_result["details"].get("processing_time_ms")
                if processing_time_ms is not None:
                    lines.append(f"**Processing Time:** {processing_time_ms/1000:.2f} seconds")

            if approach_result.get("details"):
                lines.append("")
                lines.append("**Details:**")
                lines.append("```json")
                lines.append(json.dumps(approach_result["details"], indent=2, ensure_ascii=False))
                lines.append("```")

            lines.append("")

        lines.append("---")
        lines.append("")

    # Summary statistics
    lines.append("## Summary Statistics")
    lines.append("")

    # Overall by metadata usage
    metadata_stats = {"with_metadata": {"success": 0, "failed": 0, "total": 0}, "without_metadata": {"success": 0, "failed": 0, "total": 0}}
    for result in data["results"]:
        use_metadata = result.get("use_metadata", True)
        metadata_key = "with_metadata" if use_metadata else "without_metadata"
        for approach_result in result["approaches"]:
            metadata_stats[metadata_key]["total"] += 1
            if approach_result["success"]:
                metadata_stats[metadata_key]["success"] += 1
            else:
                metadata_stats[metadata_key]["failed"] += 1

    lines.append("### Overall Statistics by Metadata Usage")
    lines.append("")
    lines.append("| Metadata | Success | Failed | Total | Success Rate |")
    lines.append("|----------|---------|--------|-------|--------------|")
    for key, stats in [("with_metadata", "With Metadata"), ("without_metadata", "Without Metadata")]:
        s = metadata_stats[key]
        success_rate = (s["success"] / s["total"] * 100) if s["total"] > 0 else 0
        lines.append(f"| {stats} | {s['success']} | {s['failed']} | {s['total']} | {success_rate:.1f}% |")
    lines.append("")

    # Per approach, split by metadata
    approach_stats = {}
    for result in data["results"]:
        use_metadata = result.get("use_metadata", True)
        metadata_key = "with_metadata" if use_metadata else "without_metadata"
        for approach_result in result["approaches"]:
            approach_name = approach_result["approach"]
            if approach_name not in approach_stats:
                approach_stats[approach_name] = {
                    "with_metadata": {"success": 0, "failed": 0, "total": 0},
                    "without_metadata": {"success": 0, "failed": 0, "total": 0},
                }
            approach_stats[approach_name][metadata_key]["total"] += 1
            if approach_result["success"]:
                approach_stats[approach_name][metadata_key]["success"] += 1
            else:
                approach_stats[approach_name][metadata_key]["failed"] += 1

    lines.append("### Per-Approach Statistics")
    lines.append("")
    lines.append("| Approach | Metadata | Success | Failed | Total | Success Rate |")
    lines.append("|----------|----------|---------|--------|-------|--------------|")
    for approach_name in sorted(approach_stats.keys()):
        for key, label in [("with_metadata", "With"), ("without_metadata", "Without")]:
            s = approach_stats[approach_name][key]
            success_rate = (s["success"] / s["total"] * 100) if s["total"] > 0 else 0
            lines.append(
                f"| {approach_name} | {label} | {s['success']} | {s['failed']} | {s['total']} | {success_rate:.1f}% |"
            )

    return "\n".join(lines)


def main():
    """Main entry point."""
    import asyncio

    script_dir = Path(__file__).parent
    default_output_dir = script_dir / "results"
    default_server_url = "http://localhost:8000"

    parser = argparse.ArgumentParser(
        description="Test a single image with the image recognition API"
    )
    parser.add_argument(
        "image",
        type=Path,
        help="Path to the image file to test",
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
        "--json-only",
        action="store_true",
        help="Only save JSON results, skip Markdown report",
    )

    args = parser.parse_args()

    # Resolve image path
    image_path = args.image
    if not image_path.is_absolute():
        image_path = (Path.cwd() / image_path).resolve()
    
    # Check if file exists
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(
        test_single_image(args.image, args.output_dir, args.server_url, args.approaches, args.json_only)
    )


if __name__ == "__main__":
    main()
