import csv
import io
import json
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, Response

from db import get_connection, init_db

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

FILTERABLE = {
    "company": "organization_name",
    "title": "title",
    "city": "city",
    "state": "state",
    "country": "country",
    "email_status": "email_status",
    "tag": None,  # handled specially (substring match on tags JSON)
}

SORTABLE = {
    "name": "full_name",
    "company": "organization_name",
    "title": "title",
    "email": "email",
    "created": "apollo_created_at",
}


def build_filters(args):
    clauses = []
    params = []

    q = args.get("q", "").strip()
    if q:
        clauses.append(
            "(full_name LIKE ? OR email LIKE ? OR organization_name LIKE ? OR title LIKE ?)"
        )
        like = f"%{q}%"
        params.extend([like, like, like, like])

    for key, column in FILTERABLE.items():
        value = args.get(key, "").strip()
        if not value:
            continue
        if key == "tag":
            clauses.append("tags LIKE ?")
            params.append(f'%"{value}"%')
        else:
            clauses.append(f"{column} = ?")
            params.append(value)

    if args.get("favorite") == "1":
        clauses.append("is_favorite = 1")

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


def row_to_dict(row):
    d = dict(row)
    d["label_ids"] = json.loads(d.get("label_ids") or "[]")
    d["tags"] = json.loads(d.get("tags") or "[]")
    d["is_favorite"] = bool(d.get("is_favorite"))
    return d


@app.get("/api/contacts")
def list_contacts():
    args = request.args
    page = max(int(args.get("page", 1)), 1)
    per_page = min(max(int(args.get("per_page", 50)), 1), 200)
    sort_key = args.get("sort", "name")
    sort_col = SORTABLE.get(sort_key, "full_name")
    order = "DESC" if args.get("order", "asc").lower() == "desc" else "ASC"

    where, params = build_filters(args)

    conn = get_connection()
    total = conn.execute(f"SELECT COUNT(*) FROM contacts {where}", params).fetchone()[0]
    rows = conn.execute(
        f"""
        SELECT * FROM contacts {where}
        ORDER BY {sort_col} COLLATE NOCASE {order}
        LIMIT ? OFFSET ?
        """,
        [*params, per_page, (page - 1) * per_page],
    ).fetchall()
    conn.close()

    return jsonify(
        {
            "total": total,
            "page": page,
            "per_page": per_page,
            "contacts": [row_to_dict(r) for r in rows],
        }
    )


@app.get("/api/contacts/<apollo_id>")
def get_contact(apollo_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM contacts WHERE apollo_id = ?", [apollo_id]).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row_to_dict(row))


@app.patch("/api/contacts/<apollo_id>")
def update_contact(apollo_id):
    body = request.get_json(force=True) or {}
    fields, params = [], []

    if "notes" in body:
        fields.append("notes = ?")
        params.append(body["notes"])
    if "tags" in body:
        fields.append("tags = ?")
        params.append(json.dumps(body["tags"]))
    if "is_favorite" in body:
        fields.append("is_favorite = ?")
        params.append(1 if body["is_favorite"] else 0)

    if not fields:
        return jsonify({"error": "no updatable fields provided"}), 400

    params.append(apollo_id)
    conn = get_connection()
    conn.execute(f"UPDATE contacts SET {', '.join(fields)} WHERE apollo_id = ?", params)
    conn.commit()
    row = conn.execute("SELECT * FROM contacts WHERE apollo_id = ?", [apollo_id]).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row_to_dict(row))


@app.get("/api/facets")
def facets():
    conn = get_connection()

    def top_values(column, limit=200):
        rows = conn.execute(
            f"""
            SELECT {column} AS value, COUNT(*) AS n FROM contacts
            WHERE {column} IS NOT NULL AND {column} != ''
            GROUP BY {column} ORDER BY n DESC LIMIT ?
            """,
            [limit],
        ).fetchall()
        return [{"value": r["value"], "count": r["n"]} for r in rows]

    data = {
        "companies": top_values("organization_name"),
        "titles": top_values("title"),
        "countries": top_values("country"),
        "email_statuses": top_values("email_status", 20),
    }
    conn.close()
    return jsonify(data)


@app.get("/api/stats")
def stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    favorites = conn.execute("SELECT COUNT(*) FROM contacts WHERE is_favorite = 1").fetchone()[0]
    with_email = conn.execute(
        "SELECT COUNT(*) FROM contacts WHERE email != ''"
    ).fetchone()[0]
    companies = conn.execute(
        "SELECT COUNT(DISTINCT organization_name) FROM contacts WHERE organization_name != ''"
    ).fetchone()[0]
    last_sync = conn.execute(
        "SELECT MAX(synced_at) FROM contacts"
    ).fetchone()[0]
    conn.close()
    return jsonify(
        {
            "total": total,
            "favorites": favorites,
            "with_email": with_email,
            "companies": companies,
            "last_synced_at": last_sync,
        }
    )


@app.get("/api/contacts.csv")
def export_csv():
    where, params = build_filters(request.args)
    conn = get_connection()
    rows = conn.execute(f"SELECT * FROM contacts {where} ORDER BY full_name COLLATE NOCASE", params).fetchall()
    conn.close()

    buf = io.StringIO()
    columns = [
        "full_name", "title", "organization_name", "email", "email_status",
        "phone", "linkedin_url", "city", "state", "country", "tags", "notes",
    ]
    writer = csv.writer(buf)
    writer.writerow(columns)
    for row in rows:
        d = row_to_dict(row)
        d["tags"] = ", ".join(d["tags"])
        writer.writerow([d.get(c, "") for c in columns])

    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"},
    )


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5050, debug=True)
