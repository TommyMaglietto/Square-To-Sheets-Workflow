"""
fetch_square_payments.py

Paginates through all payments in Square and writes them to .tmp/payments.json.
Used by write_to_google_sheets.py as a fallback for last_booked_date: when a customer
has no booking record (e.g. an appointment entered manually by staff rather than
through the booking flow), their most recent completed payment date is used instead.

Usage:
    python execution/fetch_square_payments.py

Requires:
    - .env with SQUARE_API_TOKEN set
    - pip install -r requirements.txt
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SQUARE_BASE_URL = "https://connect.squareup.com/v2"
SQUARE_VERSION  = "2026-01-22"
OUTPUT_PATH = os.path.join(".tmp", "payments.json")

# Payments endpoint requires begin_time — set far enough back to capture history.
# Adjust if your business predates this.
PAYMENTS_BEGIN_TIME = "2015-01-01T00:00:00+00:00"

load_dotenv()

TOKEN = os.getenv("SQUARE_API_TOKEN", "").strip()
if not TOKEN:
    print("ERROR: SQUARE_API_TOKEN is missing or empty in .env")
    print("       Copy .env.example to .env and paste your Square access token.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Fetch all payments (paginated)
# ---------------------------------------------------------------------------
def fetch_all_payments():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Square-Version": SQUARE_VERSION,
        "Content-Type": "application/json",
    }

    all_payments = []
    cursor = None

    while True:
        params = {
            "limit": 100,
            "begin_time": PAYMENTS_BEGIN_TIME,
        }
        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            f"{SQUARE_BASE_URL}/payments",
            headers=headers,
            params=params,
        )

        if response.status_code != 200:
            print(f"ERROR: Square API returned {response.status_code}")
            print(response.text)
            sys.exit(1)

        data = response.json()

        all_payments.extend(data.get("payments", []))

        cursor = data.get("cursor")
        if not cursor:
            break

    return all_payments


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    payments = fetch_all_payments()

    os.makedirs(".tmp", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payments, f, indent=2, ensure_ascii=False)

    print(f"Fetched {len(payments)} payments. Saved to {OUTPUT_PATH}")
