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

Open **http://127.0.0.1:5050** in your browser.

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
