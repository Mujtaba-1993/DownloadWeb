#!/usr/bin/env python3
"""One-off: merge every data/raw/contacts_part_*.ndjson file (written by the
Apollo fetch agents, in the old flat apollo_id-keyed shape) into the main
contacts.db using the current id/apollo_id schema."""
import glob
import json
import time

from db import get_connection, init_db, upsert_contact
from apollo_transform import contact_id

init_db()
conn = get_connection()
synced_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

total = 0
for path in sorted(glob.glob("data/raw/contacts_part_*.ndjson")):
    n = 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            email = (row.get("email") or "").lower()
            record = {
                "id": contact_id(email, "apollo", row.get("apollo_id") or ""),
                "apollo_id": row.get("apollo_id") or "",
                "first_name": row.get("first_name") or "",
                "last_name": row.get("last_name") or "",
                "full_name": row.get("full_name") or "",
                "title": row.get("title") or "",
                "email": email,
                "email_status": row.get("email_status") or "",
                "phone": row.get("phone") or "",
                "linkedin_url": row.get("linkedin_url") or "",
                "organization_name": row.get("organization_name") or "",
                "organization_domain": row.get("organization_domain") or "",
                "city": row.get("city") or "",
                "state": row.get("state") or "",
                "country": row.get("country") or "",
                "label_ids": json.dumps(row.get("label_ids") or []),
                "source": "apollo",
                "apollo_created_at": row.get("apollo_created_at") or "",
                "apollo_updated_at": row.get("apollo_updated_at") or "",
                "synced_at": synced_at,
            }
            upsert_contact(conn, record)
            n += 1
    conn.commit()
    total += n
    print(f"{path}: merged {n}")

print(f"TOTAL merged: {total}")
conn.close()
