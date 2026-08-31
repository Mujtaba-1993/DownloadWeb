#!/usr/bin/env python3
"""
Import contacts from spreadsheet exports (e.g. a Salesforce/BFO export, or a
manually curated account list) into Callo's local database, alongside your
Apollo contacts.

Usage:
    python import_spreadsheets.py vssr /path/to/VSSR_CONTACTS_updated.xlsx
    python import_spreadsheets.py bfo /path/to/BFO_x_Apollo_Merged_Contacts.xlsx

Both are safe to re-run. Contacts are matched by email across every source
(Apollo, VSSR, BFO, ...): if the same person already exists, the row is
merged in rather than duplicated, and the `source` field lists every place
that contact was seen (e.g. "apollo,bfo").
"""
import sys
import time
import hashlib

import openpyxl

from db import get_connection, init_db, upsert_contact
from apollo_transform import contact_id


def first(*values):
    for v in values:
        if v:
            return str(v).strip()
    return ""


def sheet_dicts(path, sheet_name):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    rows = ws.iter_rows(values_only=True)
    header = [str(h).strip() if h else "" for h in next(rows)]
    for row in rows:
        yield dict(zip(header, row))
    wb.close()


def build_record(source, full_name, title, email, email_status, phone,
                  organization_name, city, state, country, linkedin_url, synced_at):
    full_name = first(full_name)
    organization_name = first(organization_name)
    email = first(email).lower()
    fallback_key = hashlib.md5(f"{full_name}|{organization_name}".encode()).hexdigest()[:16]
    return {
        "id": contact_id(email, source, fallback_key),
        "apollo_id": "",
        "first_name": full_name.split(" ")[0] if full_name else "",
        "last_name": " ".join(full_name.split(" ")[1:]) if full_name else "",
        "full_name": full_name,
        "title": first(title),
        "email": email,
        "email_status": first(email_status),
        "phone": first(phone),
        "linkedin_url": first(linkedin_url),
        "organization_name": organization_name,
        "organization_domain": "",
        "city": first(city),
        "state": first(state),
        "country": first(country),
        "label_ids": "[]",
        "source": source,
        "apollo_created_at": "",
        "apollo_updated_at": "",
        "synced_at": synced_at,
    }


def import_vssr(path):
    synced_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn = get_connection()
    n = 0
    for row in sheet_dicts(path, "Contacts"):
        if not first(row.get("Name")):
            continue
        record = build_record(
            source="vssr",
            full_name=row.get("Name"),
            title=row.get("Title"),
            email=row.get("Email"),
            email_status=row.get("Email Status"),
            phone=first(row.get("Mobile"), row.get("Other Phone")),
            organization_name=first(row.get("Apollo Company"), row.get("Account (your list)")),
            city=row.get("City"),
            state="",
            country=row.get("Country"),
            linkedin_url=row.get("LinkedIn"),
            synced_at=synced_at,
        )
        upsert_contact(conn, record)
        n += 1
    conn.commit()
    conn.close()
    print(f"VSSR import: {n} contacts")


def import_bfo(path):
    synced_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn = get_connection()
    n = 0
    skipped_non_bfo = 0
    for row in sheet_dicts(path, "Merged Contacts"):
        if row.get("Source") != "BFO (Salesforce)":
            skipped_non_bfo += 1
            continue
        if not first(row.get("Contact Name")):
            continue
        record = build_record(
            source="bfo",
            full_name=row.get("Contact Name"),
            title=row.get("Job Title"),
            email=row.get("Email"),
            email_status=row.get("Email Status"),
            phone=first(row.get("Mobile"), row.get("Work / Other Phone")),
            organization_name=first(row.get("BFO Account Name"), row.get("Apollo Company Name")),
            city=row.get("City"),
            state="",
            country="",
            linkedin_url=row.get("LinkedIn"),
            synced_at=synced_at,
        )
        upsert_contact(conn, record)
        n += 1
    conn.commit()
    conn.close()
    print(f"BFO import: {n} contacts (skipped {skipped_non_bfo} non-BFO rows in the same sheet)")


IMPORTERS = {"vssr": import_vssr, "bfo": import_bfo}


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in IMPORTERS:
        print(f"Usage: python import_spreadsheets.py <{'|'.join(IMPORTERS)}> <path-to-xlsx>", file=sys.stderr)
        sys.exit(1)
    init_db()
    IMPORTERS[sys.argv[1]](sys.argv[2])


if __name__ == "__main__":
    main()
