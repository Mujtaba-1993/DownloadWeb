# My Contacts

A small, self-hosted, personal contact tool — a private copy of your Apollo
CRM contacts in a searchable/filterable table, similar to Apollo's contact
view, but local-only and for your own use.

It does **not** send your data anywhere. It runs entirely on your own
machine: a local SQLite database plus a small local web server.

## Setup

```bash
cd contact-tool/server
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 1. Pull your contacts from Apollo

Get a Master API key from Apollo: **Settings → Integrations → API**.

```bash
export APOLLO_API_KEY="your-key-here"
python sync_apollo.py
```

This pages through every contact your Apollo team has saved and stores it
in `server/data/contacts.db` (a local SQLite file, gitignored — never
committed). It's safe to re-run any time to refresh: contacts are matched
by their Apollo id, and any notes/tags/favorites you've added locally are
preserved.

## 2. Run the tool

```bash
python app.py
```

Open **http://127.0.0.1:5050** in your browser.

## What it does

- Searchable, sortable, filterable contact table (company, title, country,
  email status, favorites)
- Click a contact to view full details, add your own **notes** and **tags**,
  and mark **favorites** — all stored locally, independent of Apollo
- Export the current filtered view to CSV
- Live counts (total contacts, companies, last synced)

## Notes on scope and privacy

- This pulls contacts your Apollo *team* has already saved/enriched — not
  Apollo's full people database.
- Clay wasn't included: at the time this was built, the connected Clay
  workspace had no contacts to pull.
- The `data/` folder (your contacts database) is git-ignored on purpose —
  it contains real people's names, emails, and phone numbers, and should
  never be pushed to a repository, especially not a public one.
