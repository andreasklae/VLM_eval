#!/usr/bin/env python3
"""
Retry script for failed approaches in batch test results.

Detects and re-runs:
1. GPT+Search (strong + fast) — for pairs that still have failed/missing GPT+Search
2. Gemini failures (DNS errors + truncation errors) for affected pairs

Both workers run concurrently since they hit different external APIs.
Results are saved incrementally after each successful API call, so you can
safely stop (Ctrl+C) and re-run later — already-fixed pairs are skipped.

Usage:
    python rerun_failed.py                    # run retries
    python rerun_failed.py --dry-run          # detect failures only, no API calls
    python rerun_failed.py --server-url URL   # custom server URL
"""

import argparse
import asyncio
import json
import mimetypes
import shutil
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import httpx

MASTER_JSONL = Path(__file__).parent / "results" / "batch_test_results_1_master.jsonl"
TEST_IMAGES_DIR = Path(__file__).parent / "test_images"
DEFAULT_SERVER_URL = "http://localhost:8000"

# Approach name constants
GPTS_STRONG = "GPT Vision + Search (strong)"
GPTS_FAST = "GPT Vision + Search (fast)"
GEMINI_STRONG = "Gemini Vision (strong)"
GEMINI_FAST = "Gemini Vision (fast)"


def load_master_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load pretty-printed JSONL file into a list of dicts."""
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return []
    results = []
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(content):
        while pos < len(content) and content[pos] in " \t\n\r":
            pos += 1
        if pos >= len(content):
            break
        obj, end = decoder.raw_decode(content, pos)
        results.append(obj)
        pos = end
    return results


def write_master_jsonl(path: Path, results: list[dict[str, Any]]) -> None:
    """Write results back as pretty-printed JSONL."""
    with open(path, "w", encoding="utf-8") as f:
        for result in results:
            json.dump(result, f, indent=2, ensure_ascii=False)
            f.write("\n")


def build_index(results: list[dict[str, Any]]) -> dict[tuple[str, bool], int]:
    """Build a lookup from (image_filename, use_gps) -> index in results list."""
    index = {}
    for i, r in enumerate(results):
        key = (r["image_filename"], r["use_gps"])
        index[key] = i
    return index


def detect_gemini_failures(results: list[dict[str, Any]]) -> dict[tuple[str, bool], list[str]]:
    """Scan results for Gemini approach failures. Returns {(filename, use_gps): [approach_names]}."""
    failures: dict[tuple[str, bool], list[str]] = defaultdict(list)
    for r in results:
        key = (r["image_filename"], r["use_gps"])
        for a in r.get("approaches", []):
            if "Gemini" in a.get("approach", "") and not a.get("success", True):
                failures[key].append(a["approach"])
    return dict(failures)


def detect_gpt_search_needs(results: list[dict[str, Any]]) -> list[tuple[str, bool]]:
    """Return (filename, use_gps) pairs that still need GPT+Search retries.

    A pair needs retry if either GPT+Search approach is missing or has success=False.
    """
    needs = []
    for r in results:
        approach_map = {a["approach"]: a for a in r.get("approaches", [])}
        strong = approach_map.get(GPTS_STRONG)
        fast = approach_map.get(GPTS_FAST)
        needs_retry = (
            strong is None
            or fast is None
            or not strong.get("success", False)
            or not fast.get("success", False)
        )
        if needs_retry:
            needs.append((r["image_filename"], r["use_gps"]))
    return needs


def resolve_image_path(image_filename: str) -> Path:
    """Get the full path for an image filename."""
    return TEST_IMAGES_DIR / image_filename


async def call_recognize(
    client: httpx.AsyncClient,
    image_path: Path,
    server_url: str,
    approaches: str,
    use_gps: bool,
) -> dict[str, Any]:
    """Call /recognize endpoint for specific approaches. Returns the result dict."""
    url = f"{server_url}/recognize"
    params = {"use_gps": str(use_gps).lower(), "approaches": approaches}

    with open(image_path, "rb") as f:
        image_data = f.read()

    mime_type, _ = mimetypes.guess_type(image_path.name)
    if not mime_type or not mime_type.startswith("image/"):
        ext_lower = image_path.suffix.lower()
        if ext_lower in {".heic", ".heif"}:
            mime_type = "image/heic"
        else:
            mime_type = "image/jpeg"

    files = {"image": (image_path.name, image_data, mime_type)}
    response = await client.post(url, files=files, params=params)
    response.raise_for_status()
    return response.json()


def merge_approaches(master_entry: dict, new_result: dict) -> int:
    """Merge retry result approaches into the master entry. Returns count of replaced approaches."""
    master_approaches = master_entry.get("approaches", [])
    new_approaches = new_result.get("approaches", [])
    replaced = 0

    for new_a in new_approaches:
        new_name = new_a["approach"]
        found = False
        for i, old_a in enumerate(master_approaches):
            if old_a["approach"] == new_name:
                master_approaches[i] = new_a
                found = True
                replaced += 1
                break
        if not found:
            master_approaches.append(new_a)
            replaced += 1

    master_entry["approaches"] = master_approaches
    return replaced


async def gpt_search_worker(
    client: httpx.AsyncClient,
    server_url: str,
    results: list[dict[str, Any]],
    index: dict[tuple[str, bool], int],
    save_lock: asyncio.Lock,
    master_path: Path,
    gpt_search_pairs: list[tuple[str, bool]],
    dry_run: bool,
) -> tuple[int, int, int]:
    """Re-run GPT+Search for pairs that need it. Returns (ok, failed, replaced)."""
    total = len(gpt_search_pairs)
    ok = 0
    failed = 0
    replaced = 0
    approaches_str = f"{GPTS_STRONG},{GPTS_FAST}"

    for i, (filename, use_gps) in enumerate(gpt_search_pairs, 1):
        gps_label = "gps=on " if use_gps else "gps=off"
        prefix = f"[GPT+S  {i:>3}/{total}]"

        if dry_run:
            print(f"{prefix} {filename} {gps_label} ... (dry-run, skipped)")
            ok += 1
            continue

        image_path = resolve_image_path(filename)
        if not image_path.exists():
            print(f"{prefix} {filename} {gps_label} ... SKIP (file not found)")
            failed += 1
            continue

        start = time.time()
        try:
            result = await call_recognize(client, image_path, server_url, approaches_str, use_gps)
            elapsed = time.time() - start

            idents = []
            for a in result.get("approaches", []):
                name_short = "strong" if "strong" in a["approach"] else "fast"
                ident = a.get("identified", "-") or "-"
                if len(ident) > 25:
                    ident = ident[:22] + "..."
                idents.append(f"{name_short}={ident}")
            ident_str = ", ".join(idents)

            # Merge and save under lock
            async with save_lock:
                key = (filename, use_gps)
                if key in index:
                    replaced += merge_approaches(results[index[key]], result)
                write_master_jsonl(master_path, results)

            ok += 1
            print(f"{prefix} {filename} {gps_label} ... ok {elapsed:.1f}s ({ident_str})")

        except Exception as e:
            elapsed = time.time() - start
            failed += 1
            err_msg = str(e)[:100]
            print(f"{prefix} {filename} {gps_label} ... FAIL {elapsed:.1f}s ({err_msg})")

    return ok, failed, replaced


async def gemini_worker(
    client: httpx.AsyncClient,
    server_url: str,
    results: list[dict[str, Any]],
    index: dict[tuple[str, bool], int],
    gemini_failures: dict[tuple[str, bool], list[str]],
    save_lock: asyncio.Lock,
    master_path: Path,
    dry_run: bool,
) -> tuple[int, int, int]:
    """Re-run failed Gemini approaches. Returns (ok, failed, replaced)."""
    pairs = sorted(gemini_failures.keys())
    total = len(pairs)
    ok = 0
    failed = 0
    replaced = 0

    for i, (filename, use_gps) in enumerate(pairs, 1):
        gps_label = "gps=on " if use_gps else "gps=off"
        approach_names = gemini_failures[(filename, use_gps)]
        approaches_str = ",".join(approach_names)
        short_names = []
        for name in approach_names:
            if "strong" in name:
                short_names.append("strong")
            elif "fast" in name:
                short_names.append("fast")
        prefix = f"[Gemini {i:>3}/{total}]"

        if dry_run:
            print(f"{prefix} {filename} {gps_label} ... (dry-run, would retry {'+'.join(short_names)})")
            ok += 1
            continue

        image_path = resolve_image_path(filename)
        if not image_path.exists():
            print(f"{prefix} {filename} {gps_label} ... SKIP (file not found)")
            failed += 1
            continue

        start = time.time()
        try:
            result = await call_recognize(client, image_path, server_url, approaches_str, use_gps)
            elapsed = time.time() - start

            idents = []
            for a in result.get("approaches", []):
                name_short = "strong" if "strong" in a["approach"] else "fast"
                ident = a.get("identified", "-") or "-"
                if len(ident) > 25:
                    ident = ident[:22] + "..."
                idents.append(f"{name_short}={ident}")
            ident_str = ", ".join(idents)

            # Merge and save under lock
            async with save_lock:
                key = (filename, use_gps)
                if key in index:
                    replaced += merge_approaches(results[index[key]], result)
                write_master_jsonl(master_path, results)

            ok += 1
            print(f"{prefix} {filename} {gps_label} ... ok {elapsed:.1f}s ({ident_str})")

        except Exception as e:
            elapsed = time.time() - start
            failed += 1
            err_msg = str(e)[:100]
            print(f"{prefix} {filename} {gps_label} ... FAIL {elapsed:.1f}s ({err_msg})")

    return ok, failed, replaced


async def main():
    parser = argparse.ArgumentParser(description="Retry failed approaches in batch test results")
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL, help="Image recognition server URL")
    parser.add_argument("--dry-run", action="store_true", help="Detect failures and show plan without making API calls")
    parser.add_argument("--master", type=Path, default=MASTER_JSONL, help="Path to master JSONL file")
    args = parser.parse_args()

    # Load master results
    print(f"Loading master: {args.master}")
    results = load_master_jsonl(args.master)
    print(f"  {len(results)} results loaded")

    if not results:
        print("No results found. Exiting.")
        return

    index = build_index(results)

    # Detect what needs retrying (based on current state of master)
    gemini_failures = detect_gemini_failures(results)
    strong_only = sum(1 for v in gemini_failures.values() if v == [GEMINI_STRONG])
    fast_only = sum(1 for v in gemini_failures.values() if v == [GEMINI_FAST])
    both = sum(1 for v in gemini_failures.values() if len(v) == 2)

    gpt_search_pairs = detect_gpt_search_needs(results)

    print(f"\nGemini retries: {len(gemini_failures)} pairs ({strong_only} strong, {fast_only} fast, {both} both)")
    print(f"GPT+Search retries: {len(gpt_search_pairs)} pairs (of {len(results)} total)")

    if not gemini_failures and not gpt_search_pairs:
        print("\nNothing to retry! All GPT+Search and Gemini approaches are successful.")
        return

    print()

    if args.dry_run:
        print("=== DRY RUN MODE — no API calls will be made ===\n")

    # Backup once before any modifications
    if not args.dry_run:
        backup_path = args.master.with_suffix(args.master.suffix + ".bak")
        if not backup_path.exists():
            shutil.copy2(args.master, backup_path)
            print(f"Backed up: {backup_path.name}")
        else:
            print(f"Backup already exists: {backup_path.name} (keeping original)")

    # Check server health (unless dry run)
    timeout = httpx.Timeout(60.0, read=600.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        if not args.dry_run:
            try:
                health = await client.get(f"{args.server_url}/health")
                health.raise_for_status()
                print(f"Server healthy: {args.server_url}\n")
            except Exception as e:
                print(f"WARNING: Cannot reach server at {args.server_url}: {e}")
                print("Make sure the server is running. Exiting.")
                return

        # Lock for concurrent writes to the shared results list + disk
        save_lock = asyncio.Lock()

        # Run both workers concurrently
        start_time = time.time()
        (gpts_ok, gpts_fail, gpts_replaced), (gem_ok, gem_fail, gem_replaced) = await asyncio.gather(
            gpt_search_worker(client, args.server_url, results, index, save_lock, args.master, gpt_search_pairs, args.dry_run),
            gemini_worker(client, args.server_url, results, index, gemini_failures, save_lock, args.master, args.dry_run),
        )
        total_time = time.time() - start_time

    # Summary
    print(f"\n{'=' * 60}")
    print(f"GPT+Search: {gpts_ok}/{gpts_ok + gpts_fail} ok, {gpts_fail} failed")
    print(f"Gemini:     {gem_ok}/{gem_ok + gem_fail} ok, {gem_fail} failed")
    print(f"Total time: {total_time:.1f}s")

    if args.dry_run:
        print("\nDry run complete. No files modified.")
        return

    print(f"\nUpdated:   {args.master.name}")
    print(f"  Replaced {gpts_replaced} GPT+Search entries, {gem_replaced} Gemini entries")

    # Count remaining failures
    remaining = 0
    for r in results:
        for a in r.get("approaches", []):
            if not a.get("success", True):
                if "Search" in a.get("approach", "") or "Gemini" in a.get("approach", ""):
                    remaining += 1
    print(f"  Remaining GPT+Search/Gemini failures: {remaining}")


if __name__ == "__main__":
    asyncio.run(main())
