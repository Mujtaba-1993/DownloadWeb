import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "contacts.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    apollo_id           TEXT PRIMARY KEY,
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
    source              TEXT DEFAULT 'apollo',
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
    """Insert a contact, or update its Apollo-sourced fields while preserving
    the personal notes/tags/favorite fields already set locally."""
    conn.execute(
        """
        INSERT INTO contacts (
            apollo_id, first_name, last_name, full_name, title, email, email_status,
            phone, linkedin_url, organization_name, organization_domain,
            city, state, country, label_ids, source,
            apollo_created_at, apollo_updated_at, synced_at
        ) VALUES (
            :apollo_id, :first_name, :last_name, :full_name, :title, :email, :email_status,
            :phone, :linkedin_url, :organization_name, :organization_domain,
            :city, :state, :country, :label_ids, :source,
            :apollo_created_at, :apollo_updated_at, :synced_at
        )
        ON CONFLICT(apollo_id) DO UPDATE SET
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            full_name=excluded.full_name,
            title=excluded.title,
            email=excluded.email,
            email_status=excluded.email_status,
            phone=excluded.phone,
            linkedin_url=excluded.linkedin_url,
            organization_name=excluded.organization_name,
            organization_domain=excluded.organization_domain,
            city=excluded.city,
            state=excluded.state,
            country=excluded.country,
            label_ids=excluded.label_ids,
            apollo_updated_at=excluded.apollo_updated_at,
            synced_at=excluded.synced_at
        """,
        c,
    )
