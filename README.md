# Square to Google Sheets

Pulls all your customers from Square and syncs them into a Google Sheet. One command. Free. No coding knowledge required to run.

---

## What You Need

- A **Square** account (you already have one if you use Square for payments/bookings)
- A **Google** account with Google Sheets
- **Python 3** installed on your computer ([download here](https://www.python.org/downloads/) if you don't have it)

---

## Setup

### Step 1 — Download the project

Click the green **Code** button on this page, then **Download ZIP**. Unzip it somewhere on your computer.

### Step 2 — Install dependencies

Open a terminal (or Command Prompt on Windows) inside the project folder and run:

```
pip install -r requirements.txt
```

### Step 3 — Get your Square Access Token

1. Go to [developer.squareup.com](https://developer.squareup.com)
2. Log in and open your app
3. Click **Production** under Credentials
4. Copy the **Access Token**

### Step 4 — Set up Google Sheets access

Follow the guide in `directives/google_oauth_setup.md` — it walks you through the Google Cloud Console step by step. End result: a file called `credentials.json` in the project folder.

### Step 5 — Configure your .env file

1. In the project folder, find the file called `.env.example`
2. Make a copy of it and rename the copy to `.env` (remove the "example" part)
3. Open `.env` in any text editor (Notepad works fine)
4. Paste your Square Access Token after `SQUARE_API_TOKEN=`
5. Open your Google Sheet, copy the long ID from the URL (`/spreadsheets/d/**THIS PART**/edit`), and paste it after `GOOGLE_SHEET_ID=`
6. Save the file

---

## Run It

Open a terminal in the project folder and run:

```
python execution/run_pipeline.py
```

**First time only:** A browser window will pop up asking you to sign in to Google and grant access. Click through it. After that, it runs silently every time.

---

## What Happens

1. The script fetches all your customers from Square
2. It writes them into your Google Sheet with these columns:

| ID | Name | Last Name | Email | Phone | Created | Updated | Notes | Last Booked |
|---|---|---|---|---|---|---|---|---|

That's it. Run it again anytime you want to refresh your customer list. It appends new rows each time, so clear the sheet first if you want a clean sync.

---

## Cost

Nothing. Square's API is free. Google Sheets is free. All the tools used here are free and open source.

---

## Need Help?

If something isn't working, check `directives/error_handling.md` — it covers the most common issues and how to fix them. The setup guide is in `directives/google_oauth_setup.md`.
