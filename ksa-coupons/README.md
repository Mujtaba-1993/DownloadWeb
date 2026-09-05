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

#### Concrete option: Feedico's free tier

Checked several providers (Feedico, CouponAPI.org, LinkMyDeals, Strackr) —
every one of them requires creating an account, because affiliate coupon
data is only ever handed out per-publisher (that's how commission
attribution works; there's no such thing as a fully anonymous public feed
of live promo codes). The closest to "free, no strings" is
[Feedico](https://feedico.io/global-coupon-api): free tier, 1,000 API
requests/month, no credit card mentioned, aggregating 40,000+ merchants
across CJ/Awin/Impact/Admitad — though Saudi-specific merchant coverage
isn't documented, so check after signing up. To wire it in:

1. Create a free account at feedico.io and generate an API token
   (`fdco_...`).
2. Add these repo secrets:
   - `COUPON_FEED_URL` = `https://api.feedico.io/api/v1/catalog/coupons`
   - `COUPON_FEED_FORMAT` = `json`
   - `COUPON_FEED_METHOD` = `POST`
   - `COUPON_FEED_AUTH_HEADER` = `Bearer fdco_your_token_here`
   - `COUPON_FEED_BODY` = `{"pageSize": 100}`
   - `COUPON_FEED_PAGINATE` = `true`
3. Run the workflow (Actions tab → "Update KSA Coupons Data" → "Run
   workflow") and check the run log for how many entries came back.

The same `COUPON_FEED_METHOD` / `COUPON_FEED_AUTH_HEADER` / `COUPON_FEED_BODY`
/ `COUPON_FEED_PAGINATE` / `COUPON_FEED_MAX_PAGES` secrets work for any other
POST+JSON, bearer-token-authenticated feed too, not just Feedico's — a
plain `GET` CSV/JSON feed only needs `COUPON_FEED_URL` and
`COUPON_FEED_FORMAT`.

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
