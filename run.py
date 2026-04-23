#!/usr/bin/env python3
"""
Start the full iWear project (DB + app) with one command.
Requires Docker Desktop to be installed and running.

Usage (from project root):
    python run.py

Then open: http://localhost:5000
"""
import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    print("Starting iWear (Docker: db + app)...")
    print("Open http://localhost:5001 when ready.\n")
    try:
        subprocess.run(
            ["docker", "compose", "up", "--build"],
            cwd=root,
            check=False,
        )
    except FileNotFoundError:
        print("Error: Docker not found. Install Docker Desktop and try again.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
