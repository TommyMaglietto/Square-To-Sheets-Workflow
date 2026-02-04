"""
write_to_google_sheets.py

Reads customers from .tmp/customers.json and appends them to a Google Sheet.
Handles OAuth2 authentication (desktop flow) and caches the token in token.json.

Usage:
    python execution/write_to_google_sheets.py

Requires:
    - .env with GOOGLE_SHEET_ID (and optionally GOOGLE_SHEET_INDEX)
    - credentials.json in the project root (see directives/google_oauth_setup.md)
    - .tmp/customers.json produced by fetch_square_customers.py
    - pip install -r requirements.txt
"""

import json
import os
import sys

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"
CUSTOMERS_PATH = os.path.join(".tmp", "customers.json")
BOOKINGS_PATH  = os.path.join(".tmp", "bookings.json")

# Column order — must match the header row exactly
COLUMNS = [
    "id",
    "given_name",
    "family_name",
    "email_address",
    "phone_number",
    "created_at",
    "updated_at",
    "note",
    "last_booked_date",
]

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "").strip()
SHEET_INDEX = int(os.getenv("GOOGLE_SHEET_INDEX", "0"))

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
if not SHEET_ID:
    print("ERROR: GOOGLE_SHEET_ID is missing or empty in .env")
    print("       Copy .env.example to .env and paste your Google Sheet ID.")
    sys.exit(1)

if not os.path.exists(CREDENTIALS_PATH):
    print("ERROR: credentials.json not found in the project root.")
    print("       Follow directives/google_oauth_setup.md to create it.")
    sys.exit(1)

if not os.path.exists(CUSTOMERS_PATH):
    print("ERROR: .tmp/customers.json not found.")
    print("       Run fetch_square_customers.py first.")
    sys.exit(1)

if not os.path.exists(BOOKINGS_PATH):
    print("ERROR: .tmp/bookings.json not found.")
    print("       Run fetch_square_bookings.py first.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Google OAuth2 — desktop flow with token caching
# ---------------------------------------------------------------------------
def get_google_credentials():
    """Return valid Google credentials, running the browser auth flow if needed."""
    creds = None

    # Try to load cached token
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            if not creds.valid and not creds.expired:
                # Credentials object exists but isn't usable — fall through to fresh auth
                creds = None
        except Exception:
            creds = None

    # Fresh auth via browser
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        # Cache for next run
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds


# ---------------------------------------------------------------------------
# Resolve the actual tab name from the sheet index
# ---------------------------------------------------------------------------
def get_sheet_tab_name(service):
    """Look up the tab name for SHEET_INDEX so range strings are unambiguous."""
    meta = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheets = meta.get("sheets", [])

    if SHEET_INDEX >= len(sheets):
        print(f"ERROR: GOOGLE_SHEET_INDEX is {SHEET_INDEX} but the spreadsheet "
              f"only has {len(sheets)} tab(s).")
        sys.exit(1)

    return sheets[SHEET_INDEX]["properties"]["title"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Load customer and booking data
    with open(CUSTOMERS_PATH, "r", encoding="utf-8") as f:
        customers = json.load(f)

    with open(BOOKINGS_PATH, "r", encoding="utf-8") as f:
        bookings = json.load(f)

    # Build a map: customer_id -> most recent start_at (the last booked date)
    last_booked = {}
    for b in bookings:
        cid = b.get("customer_id")
        start = b.get("start_at", "")
        if cid and start:
            if start > last_booked.get(cid, ""):
                last_booked[cid] = start

    # Inject last_booked_date into each customer record
    for c in customers:
        c["last_booked_date"] = last_booked.get(c["id"], "")

    # Authenticate and build API client
    creds = get_google_credentials()
    service = build("sheets", "v4", credentials=creds)

    # Resolve tab name
    tab_name = get_sheet_tab_name(service)

    # Check if the sheet is empty (no header yet)
    existing = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SHEET_ID, range=f"'{tab_name}'!A1:I1")
        .execute()
    )
    sheet_is_empty = "values" not in existing

    # Build the rows: header (if needed) + data
    rows = []
    if sheet_is_empty:
        rows.append(COLUMNS)  # header row

    for customer in customers:
        row = [str(customer.get(col, "")) for col in COLUMNS]
        rows.append(row)

    if not rows:
        print("Nothing to write — sheet already has a header and there are no customers.")
        sys.exit(0)

    # Append
    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"'{tab_name}'!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()

    data_rows = len(rows) - (1 if sheet_is_empty else 0)
    print(f"Wrote {data_rows} customer row(s) to Google Sheet {SHEET_ID} (tab: {tab_name})")
