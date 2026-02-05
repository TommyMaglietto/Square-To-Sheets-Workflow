"""
fetch_square_bookings.py

Paginates through all bookings in Square and writes them to .tmp/bookings.json.
Used by write_to_google_sheets.py to compute each customer's last booked date.

Usage:
    python execution/fetch_square_bookings.py

Requires:
    - .env with SQUARE_API_TOKEN set
    - pip install -r requirements.txt
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SQUARE_BASE_URL = "https://connect.squareup.com/v2"
SQUARE_VERSION  = "2026-01-22"
OUTPUT_PATH = os.path.join(".tmp", "bookings.json")

# Bookings endpoint uses start_at_min / start_at_max and enforces a max
# 31-day window per request.  We slide a 30-day window from HISTORY_START
# through to HISTORY_END to collect the full range.
HISTORY_START = datetime(2024, 1, 1, tzinfo=timezone.utc)
HISTORY_END   = datetime(2027, 1, 1, tzinfo=timezone.utc)
WINDOW_DAYS   = 30

load_dotenv()

TOKEN = os.getenv("SQUARE_API_TOKEN", "").strip()
if not TOKEN:
    print("ERROR: SQUARE_API_TOKEN is missing or empty in .env")
    print("       Copy .env.example to .env and paste your Square access token.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Fetch all bookings (sliding 30-day window + pagination within each window)
# ---------------------------------------------------------------------------
def fetch_all_bookings():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Square-Version": SQUARE_VERSION,
        "Content-Type": "application/json",
    }

    all_bookings = []
    window_start = HISTORY_START

    while window_start < HISTORY_END:
        window_end = min(window_start + timedelta(days=WINDOW_DAYS), HISTORY_END)
        cursor = None

        while True:
            params = {
                "limit": 100,
                "start_at_min": window_start.isoformat(),
                "start_at_max": window_end.isoformat(),
            }
            if cursor:
                params["cursor"] = cursor

            response = requests.get(
                f"{SQUARE_BASE_URL}/bookings",
                headers=headers,
                params=params,
            )

            if response.status_code != 200:
                print(f"ERROR: Square API returned {response.status_code}")
                print(response.text)
                sys.exit(1)

            data = response.json()
            all_bookings.extend(data.get("bookings", []))

            cursor = data.get("cursor")
            if not cursor:
                break

        window_start = window_end

    return all_bookings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    bookings = fetch_all_bookings()

    os.makedirs(".tmp", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2, ensure_ascii=False)

    print(f"Fetched {len(bookings)} bookings. Saved to {OUTPUT_PATH}")
