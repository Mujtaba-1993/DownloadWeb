#!/usr/bin/env python3
"""Refreshes ksa-coupons/data/coupons.json and the embedded copy in index.html.

Run by .github/workflows/update-ksa-coupons.yml on a daily schedule. What it
does automatically, without any external data source:
  - drops coupons whose "expires" date has passed
  - bumps "generated_at" to the current UTC time so the page's
    "Last updated" label reflects a real, scheduled refresh

To pull in genuinely new deals automatically (rather than editing the JSON
by hand), replace `fetch_new_coupons()` below with calls into a real coupon
or affiliate-network API/feed and merge the results into `coupons`.
"""
import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "coupons.json"
HTML_PATH = ROOT / "index.html"
START_MARKER = "<!-- COUPONS_DATA_START -->"
END_MARKER = "<!-- COUPONS_DATA_END -->"


def fetch_new_coupons():
    """Placeholder hook for a real coupon/affiliate feed.

    Return a list of coupon dicts (same shape as entries in coupons.json)
    to merge in. Returning an empty list keeps today's run limited to
    pruning expired offers and refreshing the timestamp.
    """
    return []


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def prune_expired(data, today):
    kept = []
    for coupon in data["coupons"]:
        expires = coupon.get("expires")
        if expires:
            try:
                exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
                if exp_date < today:
                    continue
            except ValueError:
                pass
        kept.append(coupon)
    data["coupons"] = kept
    return data


def merge_new(data, new_coupons):
    existing_ids = {c["id"] for c in data["coupons"]}
    for coupon in new_coupons:
        if coupon["id"] in existing_ids:
            continue
        data["coupons"].append(coupon)
        existing_ids.add(coupon["id"])
    return data


def write_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_embedded_copy(data, html_path):
    html = html_path.read_text(encoding="utf-8")
    start = html.index(START_MARKER)
    end = html.index(END_MARKER) + len(END_MARKER)
    new_block = (
        START_MARKER
        + "\n"
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n"
        + END_MARKER
    )
    html = html[:start] + new_block + html[end:]
    html_path.write_text(html, encoding="utf-8")


def main():
    today = datetime.now(timezone.utc).date()
    data = load(DATA_PATH)

    data = prune_expired(data, today)
    data = merge_new(data, fetch_new_coupons())
    data["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    write_json(data, DATA_PATH)
    write_embedded_copy(data, HTML_PATH)
    print(f"Updated {len(data['coupons'])} coupons; generated_at={data['generated_at']}")


if __name__ == "__main__":
    main()
