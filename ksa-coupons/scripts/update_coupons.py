#!/usr/bin/env python3
"""Refreshes ksa-coupons/data/coupons.json and the embedded copy in index.html.

Run by .github/workflows/update-ksa-coupons.yml on a daily schedule. Every
run, with no configuration at all, does two things automatically:
  - drops coupons whose "expires" date has passed
  - bumps "generated_at" to the current UTC time so the page's
    "Last updated" label reflects a real, scheduled refresh

Optionally, if a COUPON_FEED_URL environment variable (set as a GitHub
Actions secret, see .github/workflows/update-ksa-coupons.yml) points at a
real coupon/affiliate feed, this script also downloads it, parses it, and
merges any new entries in. That is the only legitimate way to get broad,
always-current KSA coupon coverage without manually curating every entry:
merchants themselves don't publish machine-readable "these codes are valid
today" pages, and coupon-aggregator sites deliberately hide their codes
from scrapers. Licensed affiliate networks (Awin, Admitad, CJ Affiliate,
Impact, etc.) sell exactly this as a CSV/JSON feed to their publishers.

No feed configured -> this script silently just prunes + refreshes the
timestamp, exactly like before. Nothing here fabricates coupon data.
"""
import csv
import io
import json
import os
import pathlib
import re
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "coupons.json"
HTML_PATH = ROOT / "index.html"
START_MARKER = "<!-- COUPONS_DATA_START -->"
END_MARKER = "<!-- COUPONS_DATA_END -->"

VALID_CATEGORIES = {
    "marketplace", "fashion", "beauty", "food", "grocery",
    "travel", "home", "kids", "transport", "telecom",
}
OTHER_CATEGORY = {"id": "other", "en": "Other", "ar": "أخرى"}

# Accepted column/key names per field, most affiliate feeds use some subset
# of these (case-insensitive). Extend this if your feed uses different names.
# Includes Feedico's schema (brandName/merchantWebsiteUrl) alongside the more
# generic names used by CSV exports from other networks.
FIELD_ALIASES = {
    "store": ["store", "merchant", "advertiser", "advertisername", "brand", "shop", "brandname", "firmname"],
    "title": ["title", "offername", "name", "headline", "voucher_title"],
    "description": ["description", "terms", "details", "offerdescription"],
    "code": ["code", "voucher", "vouchercode", "promocode", "coupon_code"],
    "discount": ["discount", "discountvalue", "offer", "savings"],
    "category": ["category", "sector", "vertical", "type_of_offer"],
    "url": ["url", "link", "landing_page", "trackingurl", "deeplink", "clickurl", "merchantwebsiteurl", "offerurl"],
    "expires": ["expires", "expirydate", "end_date", "validto", "enddate"],
}

# Common wrapper keys JSON APIs use around the actual list of records
# (e.g. {"data": [...]} or {"coupons": [...]}), tried in order.
JSON_LIST_WRAPPER_KEYS = ["data", "coupons", "results", "items", "records"]


def _unwrap_json_list(parsed):
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        for key in JSON_LIST_WRAPPER_KEYS:
            if isinstance(parsed.get(key), list):
                return parsed[key]
    return []


def _request_page(feed_url, method, headers, body_obj):
    data_bytes = json.dumps(body_obj).encode("utf-8") if body_obj is not None else None
    req = urllib.request.Request(feed_url, data=data_bytes, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_new_coupons():
    """Fetch and normalize entries from COUPON_FEED_URL, if configured.

    Supports CSV (default) or JSON (COUPON_FEED_FORMAT=json). For JSON APIs
    that require an Authorization header and/or a POST body (e.g. Feedico's
    "Authorization: Bearer <token>" + POST /api/v1/catalog/coupons), set:
      COUPON_FEED_METHOD=POST
      COUPON_FEED_AUTH_HEADER="Bearer fdco_..."
      COUPON_FEED_BODY='{"pageSize": 100}'   (optional JSON object, merged
                                               with a "page" key when paginating)
      COUPON_FEED_PAGINATE=true               (loop "page" 1..COUPON_FEED_MAX_PAGES,
                                                 stopping at the first empty page)
      COUPON_FEED_MAX_PAGES=5

    Returns [] on missing config or any fetch/parse failure -- a bad or
    unreachable feed should never break the scheduled prune-and-refresh run.
    """
    feed_url = os.environ.get("COUPON_FEED_URL", "").strip()
    if not feed_url:
        return []

    feed_format = os.environ.get("COUPON_FEED_FORMAT", "csv").strip().lower()
    method = os.environ.get("COUPON_FEED_METHOD", "GET").strip().upper()
    paginate = os.environ.get("COUPON_FEED_PAGINATE", "").strip().lower() in ("1", "true", "yes")
    max_pages = int(os.environ.get("COUPON_FEED_MAX_PAGES", "5") or 5)

    headers = {"User-Agent": "ksa-coupons-updater/1.0"}
    auth_header = os.environ.get("COUPON_FEED_AUTH_HEADER", "").strip()
    if auth_header:
        headers["Authorization"] = auth_header
    if method == "POST":
        headers["Content-Type"] = "application/json"

    base_body = None
    body_raw = os.environ.get("COUPON_FEED_BODY", "").strip()
    if body_raw:
        try:
            base_body = json.loads(body_raw)
        except Exception as exc:
            print(f"WARNING: COUPON_FEED_BODY is not valid JSON ({exc}); ignoring it")

    all_rows = []
    pages = range(1, max_pages + 1) if paginate else [None]
    for page in pages:
        body_obj = None
        if method == "POST":
            body_obj = dict(base_body) if isinstance(base_body, dict) else {}
            if page is not None:
                body_obj["page"] = page

        try:
            raw = _request_page(feed_url, method, headers, body_obj)
        except Exception as exc:
            print(f"WARNING: could not fetch COUPON_FEED_URL ({exc}); skipping feed import")
            return []

        try:
            if feed_format == "json":
                page_rows = _unwrap_json_list(json.loads(raw))
            else:
                page_rows = list(csv.DictReader(io.StringIO(raw)))
        except Exception as exc:
            print(f"WARNING: could not parse coupon feed as {feed_format} ({exc}); skipping feed import")
            return []

        all_rows.extend(page_rows)
        if not paginate or not page_rows:
            break

    coupons = []
    for row in all_rows:
        coupon = normalize_row(row)
        if coupon:
            coupons.append(coupon)
    print(f"Fetched {len(coupons)} usable entries from COUPON_FEED_URL")
    return coupons


def _lookup(row, field):
    lowered = {str(k).strip().lower(): v for k, v in row.items() if v is not None}
    for alias in FIELD_ALIASES[field]:
        if alias in lowered and str(lowered[alias]).strip():
            return str(lowered[alias]).strip()
    return None


def _slugify(*parts):
    text = "-".join(p for p in parts if p).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "feed-entry"


def normalize_row(row):
    if not isinstance(row, dict):
        return None

    store = _lookup(row, "store")
    title = _lookup(row, "title") or _lookup(row, "discount")
    if not store or not title:
        return None

    code = _lookup(row, "code")
    url = _lookup(row, "url") or "#"
    category = (_lookup(row, "category") or "").lower()
    if category not in VALID_CATEGORIES:
        category = OTHER_CATEGORY["id"]

    expires = _lookup(row, "expires")
    if expires:
        expires = expires[:10]
        try:
            datetime.strptime(expires, "%Y-%m-%d")
        except ValueError:
            expires = None

    return {
        "id": _slugify("feed", store, code or title),
        "store": store,
        "storeUrl": url,
        "category": category,
        "title": title,
        "description": _lookup(row, "description") or title,
        "code": code,
        "type": "code" if code else "deal",
        "discount": _lookup(row, "discount") or title,
        "expires": expires,
        "verified_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


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
    added = 0
    for coupon in new_coupons:
        if coupon["id"] in existing_ids:
            continue
        data["coupons"].append(coupon)
        existing_ids.add(coupon["id"])
        added += 1
        if coupon["category"] == OTHER_CATEGORY["id"] and not any(
            c["id"] == OTHER_CATEGORY["id"] for c in data["categories"]
        ):
            data["categories"].append(dict(OTHER_CATEGORY))
    if added:
        print(f"Merged {added} new coupon(s) from feed")
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
