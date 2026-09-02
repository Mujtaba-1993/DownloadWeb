# Callo

A small, personal contact tool — a private, unified copy of your contacts
(Apollo, plus any spreadsheet exports like Salesforce/BFO) in a
searchable/filterable view, similar to Apollo's contact view, but for your
own use only.

Two ways to run it, both covered below: as a **standalone web app**
published privately to your own Claude account (no computer needed —
just open a link on your phone), or as a **local server** on your own
computer (a local SQLite database plus a small Flask server, reached from
your phone over Wi-Fi or Tailscale). Neither sends your data anywhere
else.

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

## 3. Use it on your iPhone

There are two fundamentally different ways to run Callo: as a standalone
web app that lives on Claude's servers (no computer involved, ever), or as
the local Flask server above, reached from your phone over your network.

### Recommended: phone-only, no computer needed

This packages the same contact tool as a single self-contained web page —
your data baked in, no server to keep running. Open a link on your phone
and it just works, like a normal web app.

```bash
cd callo/webapp
python3 build.py
```

This writes `callo/webapp/dist/callo_app.html` — **your real contact data
is embedded in that file**, so never commit it or send it anywhere except
directly to Claude to publish (next step). It's git-ignored already.

To publish it: start a Claude Code or claude.ai conversation (in an
interactive session under your own account, not a fully-automated one —
publishing needs your direct approval) and say:

> Publish this file as a Claude Artifact titled "Callo," with capabilities
> `{"db": {}, "downloads": true}`.

...attaching `callo/webapp/dist/callo_app.html`. Claude will give you back
a private link. Open it in Safari on your iPhone, then tap the Share
button → **Add to Home Screen** for a one-tap icon that opens full-screen,
like any other app.

Why this is private: an Artifact that declares the `db` capability is
tied to your Claude account and can't be shared publicly — only you (and
your organization, if you're on a Team/Enterprise plan) can open it.
Editing a contact's notes, tags, or favorite status saves into that
private per-artifact database, not anywhere else. There's no password to
remember, no server to keep running, and no network setup — just the
link.

Re-run `python3 build.py` and ask Claude to republish the same link
whenever you want to push a fresh Apollo/VSSR/BFO sync into it (this
overwrites the underlying contact data; notes/tags/favorites you added
through the app live in the Artifact's own database, not in this file, so
review whether you actually want a full resync before doing it).

### Alternative: run it yourself on a computer

If you'd rather keep everything on hardware you control instead of
Claude's Artifact hosting, use the local Flask server from steps 1-2
above and reach it from your phone one of these ways:

#### Simplest: same Wi-Fi, no apps to install

Works whenever your iPhone and computer are on the same Wi-Fi network
(e.g. at home). Nothing to install or sign up for.

1. Find your computer's address on the network:
   ```bash
   python find_lan_ip.py
   ```
   It prints something like `192.168.1.23`.
2. Run Callo bound to that address:
   ```bash
   CALLO_HOST=192.168.1.23 python app.py
   ```
3. On your iPhone, join the same Wi-Fi, then open Safari to
   `http://192.168.1.23:5050` and enter the Callo password.
4. Tap the Share button → **Add to Home Screen** for a one-tap icon.

The only tradeoff: it only works while both devices are on that same
Wi-Fi, and the password travels unencrypted over that network — fine on a
trusted home network, not something to do on public Wi-Fi. If that's good
enough, you're done — skip Tailscale entirely.

#### Works from anywhere, away from home too (Tailscale)

A bit more setup (installing an app on two devices, once), but then it
works over cellular data too, anywhere, fully encrypted. Only do this if
you actually need off-Wi-Fi access:

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
  computer's own LAN address (found via `find_lan_ip.py`) opens it to
  other devices on the *same Wi-Fi only* — fine on a trusted home network,
  not on public/shared Wi-Fi, since the password isn't encrypted over
  plain HTTP. Setting it to your Tailscale address instead keeps that
  encryption regardless of network. Never set it to `0.0.0.0` on a
  network you don't trust.
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
