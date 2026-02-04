"""
fetch_square_customers.py

Paginates through all customers in Square and writes them to .tmp/customers.json.

Usage:
    python execution/fetch_square_customers.py

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
OUTPUT_PATH = os.path.join(".tmp", "customers.json")

load_dotenv()

TOKEN = os.getenv("SQUARE_API_TOKEN", "").strip()
if not TOKEN:
    print("ERROR: SQUARE_API_TOKEN is missing or empty in .env")
    print("       Copy .env.example to .env and paste your Square access token.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Fetch all customers (paginated)
# ---------------------------------------------------------------------------
def fetch_all_customers():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Square-Version": SQUARE_VERSION,
        "Content-Type": "application/json",
    }

    all_customers = []
    cursor = None

    while True:
        params = {}
        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            f"{SQUARE_BASE_URL}/customers",
            headers=headers,
            params=params,
        )

        if response.status_code != 200:
            print(f"ERROR: Square API returned {response.status_code}")
            print(response.text)
            sys.exit(1)

        data = response.json()

        # Square omits the key entirely when no customers remain
        customers = data.get("customers", [])
        all_customers.extend(customers)

        # Pagination: cursor is absent or None when there are no more pages
        cursor = data.get("cursor")
        if not cursor:
            break

    return all_customers


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    customers = fetch_all_customers()

    # Ensure .tmp/ exists
    os.makedirs(".tmp", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(customers, f, indent=2, ensure_ascii=False)

    print(f"Fetched {len(customers)} customers. Saved to {OUTPUT_PATH}")
