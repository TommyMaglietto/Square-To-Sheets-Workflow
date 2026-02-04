"""
run_pipeline.py

Single entry-point for the Square → Google Sheets pipeline.
Runs fetch then write in order; stops immediately if either step fails.

Usage:
    python execution/run_pipeline.py

Can be invoked from anywhere — the script resolves its own project root.
"""

import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve project root (parent of execution/)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------
STEPS = [
    {
        "label": "Fetching customers from Square...",
        "script": "execution/fetch_square_customers.py",
    },
    {
        "label": "Writing to Google Sheets...",
        "script": "execution/write_to_google_sheets.py",
    },
]


def main():
    print("=== Square to Google Sheets Pipeline ===\n")

    for i, step in enumerate(STEPS, start=1):
        print(f"[Step {i}/{len(STEPS)}] {step['label']}")

        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / step["script"])],
            cwd=str(PROJECT_ROOT),  # scripts expect .env, credentials.json, .tmp/ here
        )

        if result.returncode != 0:
            print(f"\nPipeline stopped at step {i}. See error output above.")
            sys.exit(result.returncode)

        print()  # blank line between steps

    print("=== Pipeline complete ===")


if __name__ == "__main__":
    main()
