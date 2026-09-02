#!/usr/bin/env python3
"""
Builds the standalone Callo web app: bakes every contact from the local
SQLite database into callo_template.html, producing dist/callo_app.html.

That output file contains your actual contact data (names, emails, phone
numbers) and must NEVER be committed to git or shared -- it's git-ignored
on purpose. Publish it as a Claude Artifact instead (see README.md), which
keeps it private to your own Claude account.

Usage:
    cd callo/webapp
    python3 build.py
"""
import sqlite3
import json
import base64
import sys
from pathlib import Path

HERE = Path(__file__).parent
DB_PATH = HERE.parent / "server" / "data" / "contacts.db"
SHELL_PATH = HERE / "callo_template.html"
OUT_DIR = HERE / "dist"
OUT_PATH = OUT_DIR / "callo_app.html"


def main():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run the Apollo sync / spreadsheet "
              f"imports first (see README.md).", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, full_name, title, organization_name, email, email_status, "
        "phone, linkedin_url, city, state, country, source FROM contacts"
    ).fetchall()

    records = []
    for r in rows:
        d = dict(r)
        rec = {"i": d["id"], "so": d["source"] or "apollo"}
        field_map = {
            "n": "full_name", "t": "title", "o": "organization_name",
            "e": "email", "es": "email_status", "p": "phone",
            "l": "linkedin_url", "c": "city", "st": "state", "co": "country",
        }
        for short, long in field_map.items():
            if d[long]:
                rec[short] = d[long]
        records.append(rec)

    blob = json.dumps(records, separators=(",", ":"), ensure_ascii=False)
    b64 = base64.b64encode(blob.encode("utf-8")).decode("ascii")

    print(f"records: {len(records)}")
    print(f"json bytes: {len(blob.encode('utf-8')):,}")

    shell = SHELL_PATH.read_text(encoding="utf-8")
    if "__SEED_DATA_B64__" not in shell:
        print("ERROR: placeholder not found in callo_template.html", file=sys.stderr)
        sys.exit(1)

    final = shell.replace("__SEED_DATA_B64__", b64)

    OUT_DIR.mkdir(exist_ok=True)
    OUT_PATH.write_text(final, encoding="utf-8")

    print(f"final file bytes: {len(final.encode('utf-8')):,}")
    print(f"wrote: {OUT_PATH}")
    print()
    print("This file contains your real contact data -- never commit or share it.")
    print("Next: publish it as a Claude Artifact (see README.md).")


if __name__ == "__main__":
    main()
