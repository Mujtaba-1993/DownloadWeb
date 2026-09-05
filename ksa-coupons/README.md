# KSA Coupons & Offers

A single-file HTML tool that lists ongoing coupons and offers from major
Saudi Arabia retailers, grouped by category (marketplaces, fashion, beauty,
food delivery, groceries, travel, home, kids, transport, telecom).

## Using it

Open `index.html` directly in a browser, or host the whole `ksa-coupons/`
folder (e.g. GitHub Pages). Features:

- Search, category filter, store filter, and sort (expiring soon / newest / store A–Z)
- Copy-to-clipboard for code-based offers, direct links for deal-based offers
- English/Arabic UI toggle with RTL layout
- Light/dark theme
- Works offline (data is embedded in the page) and auto-picks up
  `data/coupons.json` when served over http(s), if that file is newer

## How the data stays current

`data/coupons.json` is the single source of truth; the same JSON is also
embedded in `index.html` between the `COUPONS_DATA_START`/`COUPONS_DATA_END`
markers so the page works even opened as a local file.

`.github/workflows/update-ksa-coupons.yml` runs `scripts/update_coupons.py`
daily. Each run:

1. Drops any coupon whose `expires` date has passed.
2. Bumps `generated_at` to the current time.
3. Writes the result back to both `data/coupons.json` and the embedded
   block in `index.html`, and commits if anything changed.

This keeps the tool honestly current (no stale/expired offers, real "last
updated" timestamp) without a manual step. It does **not** by itself invent
brand-new coupons — there is no free, reliable, public API that covers
"all coupons in KSA, all types." To make brand-new deals appear
automatically, implement `fetch_new_coupons()` in
`scripts/update_coupons.py` against a real data source, for example:

- A coupon/affiliate network you have access to (Admitad, CJ Affiliate,
  Awin, etc.) that exposes a feed or API for its Saudi merchants.
- A merchant's own public deals/promotions API, where one exists.

Until then, add or edit entries directly in `data/coupons.json` (the
nightly job will pick up your edits, prune them once they expire, and keep
the embedded copy in `index.html` in sync).

### Coupon entry shape

```json
{
  "id": "unique-slug",
  "store": "Store Name",
  "storeUrl": "https://example.com/",
  "category": "marketplace | fashion | beauty | food | grocery | travel | home | kids | transport | telecom",
  "title": "Short offer title",
  "description": "One or two sentence description",
  "code": "PROMOCODE or null",
  "type": "code | deal",
  "discount": "Display string, e.g. '20% off'",
  "expires": "YYYY-MM-DD or null for ongoing",
  "verified_at": "YYYY-MM-DD"
}
```
