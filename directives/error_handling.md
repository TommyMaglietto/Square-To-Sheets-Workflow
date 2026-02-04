# Error Handling Reference

## Purpose
Catalogue of errors this pipeline can hit, their likely causes, and exact recovery steps.
This file is a living document — update it whenever a new error is encountered and resolved.

---

## Square API Errors

### 401 Unauthorized
- **Cause:** `SQUARE_API_TOKEN` is missing, empty, or invalid.
- **Fix:** Check `.env`. Paste a valid access token. Production tokens do not expire; sandbox tokens may.

### 429 Too Many Requests
- **Cause:** Rate limit hit. Square's limit is generous for list endpoints but can be triggered in tight loops.
- **Fix:** Add a 1–2 second sleep between paginated requests and retry.

### 500 / 503 Server Error
- **Cause:** Square-side outage.
- **Fix:** Retry after 5 seconds, up to 3 attempts. If it persists, check https://status.squareup.com.

---

## Google Sheets API Errors

### 403 Forbidden — "The caller does not have permission"
- **Cause (most common):** The Sheets API is not enabled on the Google Cloud project.
- **Fix:** Go to Google Cloud Console, confirm the Sheets API is enabled (see `directives/google_oauth_setup.md` Step 2).
- **Cause (second):** OAuth consent screen was set to External and your email was not added as a test user.
- **Fix:** Go to OAuth consent screen → Test Users, add your email.

### 403 Forbidden — "Access denied"
- **Cause:** `token.json` is stale or was generated under a different consent screen configuration.
- **Fix:** Delete `token.json` from the project root. Re-run the script — it will trigger a fresh browser authorization.

### 400 Bad Request — "Invalid values"
- **Cause:** A `None`/`null` value ended up in a row array. Google Sheets API rejects nulls.
- **Fix:** Check `write_to_google_sheets.py` — every field must default to `""`, never `None`.

### FileNotFoundError: credentials.json
- **Cause:** The file was not downloaded or was placed in the wrong directory.
- **Fix:** Follow `directives/google_oauth_setup.md` from Step 4 onward.

---

## Pipeline-Level Errors

### FileNotFoundError: .tmp/customers.json
- **Cause:** `fetch_square_customers.py` was not run before `write_to_google_sheets.py`, or it failed silently.
- **Fix:** Run `fetch_square_customers.py` first, or use `run_pipeline.py` which enforces ordering.

### .env file not found / variable missing
- **Cause:** `.env` was not created from `.env.example`.
- **Fix:** Copy `.env.example` to `.env` and fill in the actual values.

---

## Self-Annealing Log

### 2026-02-04 — Wrong base URL (404 on all endpoints)
- **Symptom:** Every Square API endpoint returned `404 {}` regardless of path or auth.
- **Root cause:** Base URL was `https://api.squareup.com` — the correct URL is `https://connect.squareup.com`. Additionally, the `Square-Version` header (e.g. `2026-01-22`) is required on every request.
- **Fix:** Updated `fetch_square_customers.py` to use `connect.squareup.com` and include `Square-Version` header. Endpoint is `GET /v2/customers` (not `/v2/customers/list`).
- **Note:** `api.squareup.com` does resolve and returns Square/Cloudflare headers, which made this hard to diagnose. Always verify against Square's docs at `developer.squareup.com/reference/square`.
