#!/usr/bin/env python3
"""
CLI script for image recognition.

Usage:
    python run_recognition.py path/to/image.jpg
    python run_recognition.py path/to/image.jpg --json
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Load .env file if present
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# Add parent to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_recognition.runner import recognize_image, get_all_approaches, get_available_approaches


def format_result_text(results: list) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("IMAGE RECOGNITION RESULTS")
    lines.append("=" * 60)

    for result in results:
        lines.append("")
        lines.append(f"Approach: {result.approach}")
        lines.append("-" * 40)

        if result.error:
            lines.append(f"  ERROR: {result.error}")
        elif result.identified:
            lines.append(f"  Identified: {result.identified}")
            if result.confidence is not None:
                lines.append(f"  Confidence: {result.confidence:.1%}")
            if result.details:
                lines.append(f"  Details:")
                for key, value in result.details.items():
                    # Truncate long values
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    lines.append(f"    {key}: {value_str}")
        else:
            lines.append("  No identification")

    lines.append("")
    lines.append("=" * 60)

    # Summary
    successful = [r for r in results if r.success]
    lines.append(f"Summary: {len(successful)}/{len(results)} approaches succeeded")

    if successful:
        lines.append("\nIdentifications:")
        for r in successful:
            conf = f" ({r.confidence:.0%})" if r.confidence else ""
            lines.append(f"  - [{r.approach}] {r.identified}{conf}")

    return "\n".join(lines)


def format_result_json(results: list) -> str:
    """Format results as JSON."""
    data = []
    for result in results:
        data.append(
            {
                "approach": result.approach,
                "identified": result.identified,
                "confidence": result.confidence,
                "details": result.details,
                "error": result.error,
                "success": result.success,
            }
        )
    return json.dumps(data, indent=2, ensure_ascii=False)


async def main():
    parser = argparse.ArgumentParser(
        description="Identify landmarks/artwork in images using multiple approaches."
    )
    parser.add_argument("image", type=Path, help="Path to the image file")
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    parser.add_argument(
        "--list-approaches",
        action="store_true",
        help="List available approaches and exit",
    )

    args = parser.parse_args()

    if args.list_approaches:
        all_approaches = get_all_approaches()
        available_approaches = get_available_approaches()
        if all_approaches:
            print("All approaches:")
            for a in all_approaches:
                status = "✓ available" if a in available_approaches else "✗ not available"
                print(f"  - {a.name} ({status})")
        else:
            print("No approaches found.")
        print("\nRequired environment variables:")
        print("  - AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY (for GPT Vision)")
        print("  - OPENAI_DIRECT_API_KEY (for GPT Vision + Search web search)")
        print("  - GOOGLE_APPLICATION_CREDENTIALS (for Google Cloud Vision)")
        return

    if not args.image.exists():
        print(f"Error: Image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    # Get all approaches - they will handle their own availability checks and return errors if needed
    approaches = get_all_approaches()
    if not approaches:
        print("Error: No recognition approaches found.", file=sys.stderr)
        sys.exit(1)

    print(f"Running {len(approaches)} approach(es) on: {args.image}", file=sys.stderr)
    print(f"Approaches: {', '.join(a.name for a in approaches)}", file=sys.stderr)
    print("", file=sys.stderr)

    # Run all approaches - they will return errors if not available
    results = await recognize_image(args.image, approaches=approaches)

    if args.json:
        print(format_result_json(results))
    else:
        print(format_result_text(results))


if __name__ == "__main__":
    asyncio.run(main())
