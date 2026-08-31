# Callo

A small, self-hosted, personal contact tool — a private, unified copy of
your contacts (Apollo, plus any spreadsheet exports like Salesforce/BFO)
in a searchable/filterable table, similar to Apollo's contact view, but
local-only and for your own use.

It does **not** send your data anywhere. It runs entirely on your own
machine: a local SQLite database plus a small local web server.

## Setup

```bash
cd callo/server
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 1. Bring in your contacts

### Apollo

Get a Master API key from Apollo: **Settings → Integrations → API**.

```bash
export APOLLO_API_KEY="your-key-here"
python sync_apollo.py
```

This pages through every contact your Apollo team has saved and stores it
in `server/data/contacts.db` (a local SQLite file, gitignored — never
committed). Safe to re-run any time to refresh.

### Spreadsheet imports (Salesforce/BFO exports, curated account lists, ...)

```bash
python import_spreadsheets.py vssr /path/to/VSSR_CONTACTS_updated.xlsx
python import_spreadsheets.py bfo  /path/to/BFO_x_Apollo_Merged_Contacts.xlsx
```

Every source is matched and merged by **email**: if a contact already
exists (say, from Apollo), importing the same person from a spreadsheet
merges into that one record and adds to its `source` list (e.g.
`apollo,bfo`) instead of creating a duplicate. A merge never blanks out a
field that's already known — it only fills gaps or adds a new source.
Keep the spreadsheet files themselves outside of git too; only place them
somewhere local before running the importer.

## 2. Run the tool

```bash
python app.py
```

The first time it runs, it prints a password:

```
Callo password: ZsjGEqqZKpbBX4QP6mkj0egj
```

Open **http://127.0.0.1:5050** — your browser will prompt for a username
(anything) and password (the one printed above). Enter it once; the
browser remembers it for the session.

To set your own password instead of the generated one, set `CALLO_PASSWORD`
before running `app.py`. Either way it's saved to `server/data/.auth`
(0600 permissions) so it stays the same across restarts.

## 3. Use it on your iPhone, from anywhere (Tailscale)

Callo defaults to `127.0.0.1` — only reachable from the computer it's
running on. To reach it from your iPhone, even away from home, put it on
your own private [Tailscale](https://tailscale.com) network instead of
opening it to the public internet:

1. Install Tailscale on the computer running Callo: <https://tailscale.com/download>.
   Sign in (free for personal use) and turn it on.
2. Install the **Tailscale** app from the App Store on your iPhone, and
   sign in with the same account. Turn the VPN toggle on.
3. On the computer, find its Tailscale address:
   ```bash
   tailscale ip -4
   ```
   It looks like `100.x.y.z`.
4. Run Callo bound to that address instead of localhost:
   ```bash
   CALLO_HOST=100.x.y.z python app.py
   ```
5. On your iPhone (with the Tailscale toggle on), open Safari to
   `http://100.x.y.z:5050` and enter the Callo password. It works the same
   whether you're on the same Wi-Fi or on cellular data anywhere else —
   Tailscale tunnels the connection to your computer either way.
6. Optional: tap the Share button in Safari → **Add to Home Screen** for a
   full-screen, app-like icon.

Why this is safe: Tailscale is a private mesh VPN — traffic is end-to-end
encrypted, and only devices you've signed into *your* Tailscale account can
even address `100.x.y.z`. It's invisible and unreachable to everyone else,
including other people on the same Wi-Fi. Callo's own password is still
required on top of that. Your computer needs to be on and awake for your
phone to reach it.

## Security — who can reach your contacts

- By default the server only binds to `127.0.0.1` (localhost) — nothing
  outside this machine can connect to it. Setting `CALLO_HOST` to your
  Tailscale address (above) is the recommended way to widen that, since
  Tailscale itself is what keeps it private. Don't set it to `0.0.0.0`
  or your plain LAN IP — that would make it reachable (Basic Auth
  credentials and all, unencrypted) by anyone else on the same Wi-Fi.
- Every request — the page itself and every API call — requires the
  password above. No password, wrong password, and you get a 401 with no
  data.
- `server/data/` (the database and the password file) is created with
  `chmod 700`; the database and password files themselves are `chmod 600`
  — unreadable by other accounts on a shared machine.
- The debug server's interactive debugger is off by default. Only enable
  it (`CALLO_DEBUG=1 python app.py`) while you're actively developing —
  it lets anyone who can reach the server run arbitrary code.

## What it does

- Searchable, sortable, filterable contact table (company, title, country,
  email status, source, favorites)
- Click a contact to view full details, add your own **notes** and **tags**,
  and mark **favorites** — all stored locally, independent of any source
- Export the current filtered view to CSV
- Live counts (total contacts, companies, breakdown by source, last synced)

## Notes on scope and privacy

- Apollo sync pulls contacts your Apollo *team* has already saved/enriched
  — not Apollo's full people database.
- Clay wasn't included: at the time this was built, the connected Clay
  workspace had no contacts to pull.
- The `data/` folder (your contacts database, and any spreadsheets you drop
  in for importing) is git-ignored on purpose — it contains real people's
  names, emails, and phone numbers, and should never be pushed to a
  repository, especially not a public one.
