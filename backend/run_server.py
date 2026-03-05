#!/usr/bin/env python3
"""
Start the image recognition FastAPI server.

Usage:
    python run_server.py
    python run_server.py --host 0.0.0.0 --port 8000
    python run_server.py --reload  # For development
"""

import argparse
import sys
from pathlib import Path

# Add backend directory to path so image_recognition can be imported
backend_path = (Path(__file__).parent.parent).resolve()
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import uvicorn


def main():
    """Start the FastAPI server with uvicorn."""
    parser = argparse.ArgumentParser(description="Start the image recognition API server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    args = parser.parse_args()

    print(f"Starting image recognition API server on http://{args.host}:{args.port}")
    if args.reload:
        print("Auto-reload enabled (development mode)")
    print("")

    uvicorn.run(
        "image_recognition.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
