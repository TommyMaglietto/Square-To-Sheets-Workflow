# Square Customers → Google Sheets — Master SOP

## Goal
Pull all customers from the Square API and write them to a Google Sheet.

---

## Prerequisites
Before running the pipeline, all of these must be true:
- [ ] `.env` exists and is populated (copy from `.env.example`, fill in values)
- [ ] `credentials.json` has been downloaded and placed in the project root (follow `directives/google_oauth_setup.md`)
- [ ] Dependencies are installed: `pip install -r requirements.txt`
- [ ] Target Google Sheet exists (can be empty — the script will write the header row automatically)

---

## Inputs
| Variable | Source | Required |
|---|---|---|
| `SQUARE_API_TOKEN` | `.env` | Yes |
| `GOOGLE_SHEET_ID` | `.env` | Yes — the long ID from the Sheet URL: `/spreadsheets/d/<ID>/edit` |
| `GOOGLE_SHEET_INDEX` | `.env` | No — defaults to `0` (first tab) |

---

## Execution Order

### Option A: Single command (recommended)
```
python execution/run_pipeline.py
```

### Option B: Step by step
```
python execution/fetch_square_customers.py
python execution/fetch_square_bookings.py
python execution/fetch_square_payments.py
python execution/write_to_google_sheets.py
```

### What each step does

**Step 1 — `fetch_square_customers.py`**
- Reads `SQUARE_API_TOKEN` from `.env`
- Paginates through all customers via `GET /v2/customers` on `connect.squareup.com`
- Writes the full list to `.tmp/customers.json`
- Prints the number of customers fetched

**Step 2 — `fetch_square_bookings.py`**
- Reads `SQUARE_API_TOKEN` from `.env`
- Paginates through all bookings via `GET /v2/bookings` on `connect.squareup.com`
- Excludes cancelled bookings (`CANCELLED_BY_CUSTOMER`, `CANCELLED_BY_SELLER`)
- Writes the filtered list to `.tmp/bookings.json`
- Prints the number of bookings fetched

**Step 3 — `fetch_square_payments.py`**
- Reads `SQUARE_API_TOKEN` from `.env`
- Paginates through all payments via `GET /v2/payments` on `connect.squareup.com`
- Writes the full list to `.tmp/payments.json`
- Prints the number of payments fetched
- **Why:** Staff can enter appointments manually (without using the booking flow). Those show up as payments but never as bookings. This step captures them so no one falls off the `last_booked_date` column.

**Step 4 — `write_to_google_sheets.py`**
- Reads `.tmp/customers.json`, `.tmp/bookings.json`, and `.tmp/payments.json`
- Merges bookings and payments into customers: for each customer, takes whichever is more recent — the most recent booking `start_at` or the most recent completed payment `created_at` — and writes it as `last_booked_date`
- Reads `GOOGLE_SHEET_ID` and `GOOGLE_SHEET_INDEX` from `.env`
- Authenticates via OAuth2 (browser popup on first run; silent on subsequent runs using cached `token.json`)
- Writes the header row if the sheet is empty
- Appends all customer rows
- Prints the number of rows written

---

## Outputs
- **Deliverable:** Google Sheet populated with customer data
- **Intermediate:** `.tmp/customers.json` — can be inspected for debugging; regenerated on every run

---

## Google Sheet Column Layout
| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| id | given_name | family_name | email_address | phone_number | created_at | updated_at | note | last_booked_date |

---

## Edge Cases
- **No customers:** Square returns an empty list. The script writes the header row only.
- **Sheet already has data:** Rows are **appended**, not overwritten. Clear the sheet first if you want a fresh sync.
- **token.json stops working:** Delete it and re-run. The browser auth popup will reappear.
- **Manually entered appointments:** Staff can create appointments outside the booking flow (e.g. directly in the dashboard or terminal). These never create a booking record, so the Bookings API misses them. The Payments API catches them — `last_booked_date` uses whichever is more recent: the last booking or the last completed payment.
- **Large accounts (10,000+ customers):** Square paginates in batches of 100. The fetch step will take multiple seconds. Payments may be a large dataset — same pagination applies.
- **Errors:** See `directives/error_handling.md` for specific error codes and recovery steps.
