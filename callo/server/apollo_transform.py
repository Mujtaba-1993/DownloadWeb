import json


def best_phone(contact: dict) -> str:
    for number in contact.get("phone_numbers") or []:
        value = number.get("sanitized_number") or number.get("raw_number")
        if value:
            return value
    return ""


def contact_id(email: str, source: str, fallback_key: str) -> str:
    """A stable id: contacts sharing an email merge across sources; without
    an email, fall back to a per-source key so records stay distinct."""
    email = (email or "").strip().lower()
    if email:
        return f"email:{email}"
    return f"{source}:{fallback_key}"


def flatten(contact: dict, synced_at: str) -> dict:
    org = contact.get("organization") or contact.get("account") or {}
    email = contact.get("email") or ""
    return {
        "id": contact_id(email, "apollo", contact.get("id") or ""),
        "apollo_id": contact.get("id") or "",
        "first_name": contact.get("first_name") or "",
        "last_name": contact.get("last_name") or "",
        "full_name": contact.get("name") or " ".join(
            filter(None, [contact.get("first_name"), contact.get("last_name")])
        ),
        "title": contact.get("title") or "",
        "email": email,
        "email_status": contact.get("email_status") or "",
        "phone": best_phone(contact),
        "linkedin_url": contact.get("linkedin_url") or "",
        "organization_name": contact.get("organization_name") or org.get("name") or "",
        "organization_domain": org.get("primary_domain") or org.get("domain") or "",
        "city": contact.get("city") or "",
        "state": contact.get("state") or "",
        "country": contact.get("country") or "",
        "label_ids": json.dumps(contact.get("label_ids") or []),
        "source": "apollo",
        "apollo_created_at": contact.get("created_at") or "",
        "apollo_updated_at": contact.get("updated_at") or "",
        "synced_at": synced_at,
    }
