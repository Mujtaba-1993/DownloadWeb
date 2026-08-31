#!/usr/bin/env python3
"""
Pulls every contact your Apollo team has saved into the local SQLite database
used by this tool. Run it yourself, any time, to (re)populate or refresh your
data -- it talks directly to Apollo's API and never sends your data anywhere
else.

Setup:
    1. Get a Master API key from Apollo: Settings -> Integrations -> API.
    2. export APOLLO_API_KEY="your-key-here"
    3. pip install -r requirements.txt
    4. python sync_apollo.py

Safe to re-run: contacts are upserted by their Apollo id, and any notes/tags/
favorites you've added locally are preserved.
"""
import os
import sys
import time

import requests

from db import get_connection, init_db, upsert_contact
from apollo_transform import flatten

API_URL = "https://api.apollo.io/api/v1/contacts/search"
PER_PAGE = 100
MAX_RETRIES = 3


def fetch_page(api_key: str, page: int) -> dict:
    payload = {
        "page": page,
        "per_page": PER_PAGE,
        "sort_by_field": "contact_created_at",
        "sort_ascending": True,
    }
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    for attempt in range(1, MAX_RETRIES + 1):
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code in (429, 500, 502, 503) and attempt < MAX_RETRIES:
            time.sleep(2 * attempt)
            continue
        resp.raise_for_status()
    raise RuntimeError(f"Failed to fetch page {page} after {MAX_RETRIES} attempts")


def main():
    api_key = os.environ.get("APOLLO_API_KEY")
    if not api_key:
        print("ERROR: set APOLLO_API_KEY in your environment first.", file=sys.stderr)
        sys.exit(1)

    init_db()
    conn = get_connection()
    synced_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    first = fetch_page(api_key, 1)
    total_pages = first["pagination"]["total_pages"]
    total_entries = first["pagination"]["total_entries"]
    print(f"Apollo reports {total_entries} contacts across {total_pages} pages.")

    def store(page_data):
        for contact in page_data.get("contacts", []):
            upsert_contact(conn, flatten(contact, synced_at))
        conn.commit()

    store(first)
    print(f"Page 1/{total_pages} done ({len(first.get('contacts', []))} contacts)")

    for page in range(2, total_pages + 1):
        data = fetch_page(api_key, page)
        store(data)
        print(f"Page {page}/{total_pages} done ({len(data.get('contacts', []))} contacts)")

    conn.close()
    print("Sync complete.")


if __name__ == "__main__":
    main()
