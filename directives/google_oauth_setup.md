# Google OAuth Setup Guide

## Goal
Get a `credentials.json` file so the pipeline can write to Google Sheets on your behalf.

## What You Will End Up With
- `credentials.json` in the project root (downloaded from Google)
- A Google Cloud project with the Sheets API enabled
- An OAuth 2.0 client configured for desktop use

---

## Steps

### Step 1: Create a Google Cloud Project
1. Go to https://console.cloud.google.com
2. Click **"Select a project"** in the top-left header bar.
3. Click **"+ CREATE PROJECT"**.
4. Enter a project name (e.g. `SquareToSheets`). The project ID auto-populates.
5. Click **CREATE**. Wait for it to finish.

### Step 2: Enable the Google Sheets API
1. In the left sidebar, click **APIs & Services** → **Library**.
2. In the search box, type `Google Sheets API`.
3. Click on the **Google Sheets API** card.
4. Click the blue **ENABLE** button.
5. Wait for the page to reload. You should see a **Manage** button — this confirms it is enabled.

### Step 3: Configure the OAuth Consent Screen
1. In the left sidebar, click **APIs & Services** → **OAuth consent screen**.
2. Select **Internal** as the user type. (If Internal is not available because this is a personal/free account, select **External**.)
3. Click **CREATE**.
4. Fill in the required fields:
   - **App name:** SquareToSheets
   - **User support email:** your email
   - **Developer contact email:** your email
5. Leave everything else at defaults. Click **SAVE AND CONTINUE**.
6. On the **Scopes** screen, click **ADD OR REMOVE SCOPES**.
7. In the filter box, type `sheets`.
8. Check the box next to `https://www.googleapis.com/auth/spreadsheets`.
9. Click **UPDATE**. Then click **SAVE AND CONTINUE**.
10. If you chose **External** in step 2, you will see a **Test users** screen. Add your own email address. Click **SAVE AND CONTINUE**.
11. Click **BACK TO DASHBOARD**.

### Step 4: Create the OAuth 2.0 Client Credential
1. In the left sidebar, click **APIs & Services** → **Credentials**.
2. Click the **+ CREATE CREDENTIALS** dropdown at the top.
3. Select **OAuth 2.0 Client ID**.
4. Set **Application type** to **Desktop application**.
5. Enter a name (e.g. `SquareToSheets Desktop`).
6. Click **CREATE**.
7. A popup appears with your Client ID and Client Secret. Click **DOWNLOAD JSON**.
8. Click **OK** to close the popup.

### Step 5: Place the File
1. Find the downloaded file (named something like `client_secret_XXXX.apps.googleusercontent.com.json`).
2. Rename it to exactly: `credentials.json`
3. Move it to the project root (the same folder as `CLAUDE.md`).

---

## Verification
Open a terminal in the project root and run:
```
python -c "import json; print(json.load(open('credentials.json')).keys())"
```
You should see: `dict_keys(['installed'])`

If you see `'web'` instead of `'installed'`, you created a Web application client instead of Desktop. Go back to Step 4 and create a new one with **Desktop application** selected.

---

## Common Mistakes
- **Wrong credential type:** Downloading a Web client instead of Desktop. Check for `"installed"` vs `"web"` in the JSON.
- **Sheets API not enabled:** You will get a 403 error at runtime. Confirm Step 2 was completed.
- **Missing test user (External consent screen):** If you chose External in Step 3, you must add your email as a test user. You will get a 403 "access denied" otherwise.
