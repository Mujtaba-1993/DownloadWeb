import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "contacts.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    id                   TEXT PRIMARY KEY,  -- 'email:<lower email>' when known, else '<source>:<hash>'
    apollo_id            TEXT,              -- Apollo's own contact id, when this record came from Apollo
    first_name          TEXT,
    last_name           TEXT,
    full_name           TEXT,
    title               TEXT,
    email               TEXT,
    email_status        TEXT,
    phone               TEXT,
    linkedin_url        TEXT,
    organization_name   TEXT,
    organization_domain TEXT,
    city                TEXT,
    state               TEXT,
    country             TEXT,
    label_ids           TEXT,       -- JSON array, Apollo's own list membership
    source              TEXT DEFAULT 'apollo',  -- comma-separated: apollo, vssr, bfo
    apollo_created_at   TEXT,
    apollo_updated_at   TEXT,
    synced_at           TEXT,
    -- personal-use fields, never overwritten by a re-sync
    notes               TEXT DEFAULT '',
    tags                TEXT DEFAULT '[]',
    is_favorite         INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(full_name);
CREATE INDEX IF NOT EXISTS idx_contacts_org ON contacts(organization_name);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_title ON contacts(title);
CREATE INDEX IF NOT EXISTS idx_contacts_favorite ON contacts(is_favorite);
"""

# Fields that get merged non-destructively: a re-sync or a second source
# fills in a blank, but never blanks out a value that's already known.
_MERGE_FIELDS = [
    "apollo_id", "first_name", "last_name", "full_name", "title", "email",
    "email_status", "phone", "linkedin_url", "organization_name",
    "organization_domain", "city", "state", "country", "label_ids",
    "apollo_created_at", "apollo_updated_at", "synced_at",
]


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def upsert_contact(conn, c: dict):
    """Insert a contact, or merge it into an existing row with the same id
    (typically the same email seen from a different source). Merging never
    blanks out a value that's already known, and combines the `source` list
    instead of overwriting it. Personal notes/tags/favorite are untouched."""
    merge_sets = ", ".join(
        f"{field}=CASE WHEN excluded.{field} IS NOT NULL AND excluded.{field} != '' "
        f"THEN excluded.{field} ELSE contacts.{field} END"
        for field in _MERGE_FIELDS
    )
    conn.execute(
        f"""
        INSERT INTO contacts (
            id, apollo_id, first_name, last_name, full_name, title, email, email_status,
            phone, linkedin_url, organization_name, organization_domain,
            city, state, country, label_ids, source,
            apollo_created_at, apollo_updated_at, synced_at
        ) VALUES (
            :id, :apollo_id, :first_name, :last_name, :full_name, :title, :email, :email_status,
            :phone, :linkedin_url, :organization_name, :organization_domain,
            :city, :state, :country, :label_ids, :source,
            :apollo_created_at, :apollo_updated_at, :synced_at
        )
        ON CONFLICT(id) DO UPDATE SET
            {merge_sets},
            source=CASE
                WHEN instr(','||contacts.source||',', ','||excluded.source||',') > 0
                THEN contacts.source
                ELSE contacts.source || ',' || excluded.source
            END
        """,
        c,
    )
