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
updated" timestamp) without a manual step.

### Why it doesn't scrape retailer or coupon-aggregator sites

Two approaches were tried and ruled out, for concrete reasons:

- **Retailer sites** (Danube, Jarir, eXtra, ...) don't publish a page
  listing which codes are currently valid — the promo box only exists at
  checkout. Their homepages are also client-rendered (React/Vue), so a
  plain HTTP fetch sees none of the actual banner/deal content anyway.
- **Coupon-aggregator sites** (Almowafir and similar) do list codes, but
  deliberately hide the code string behind a click-to-reveal interaction
  specifically to stop scraping and force traffic through their site.
  Defeating that is a ToS violation and isn't something this project does.

### Getting real, broad, automatic coverage: COUPON_FEED_URL

The legitimate way to get "all coupons" style coverage is a licensed
coupon/affiliate network feed (Awin, Admitad, CJ Affiliate, Impact, and
similar all sell exactly this to their publishers as a CSV or JSON export).
Once you have one:

1. In the repo's GitHub Settings → Secrets and variables → Actions, add:
   - `COUPON_FEED_URL` — the feed's URL (include your API token/query
     param if the network requires one in the URL).
   - `COUPON_FEED_FORMAT` — `csv` (default) or `json`.
2. The next scheduled (or manually triggered, via the Actions tab's
   "Run workflow" button) run of `update-ksa-coupons.yml` downloads it,
   normalizes recognized columns (store/merchant, title, code, discount,
   category, url, expires — see `FIELD_ALIASES` in
   `scripts/update_coupons.py` for exact accepted header names), dedupes
   against existing entries by `id`, and merges the rest in automatically.
   A row whose category doesn't match one of the built-in categories is
   filed under an auto-added "Other" category rather than dropped.
3. If the feed is unreachable or malformed, the script logs a warning and
   falls back to just pruning + refreshing the timestamp — a bad feed
   never breaks the scheduled run.

No feed configured -> nothing changes from the default behavior. Until you
have one, entries can also be added or edited directly in
`data/coupons.json` (the nightly job picks up manual edits, prunes them
once they expire, and keeps the embedded copy in `index.html` in sync).

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
