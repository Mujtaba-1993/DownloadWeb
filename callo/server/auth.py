import hmac
import os
import secrets
from pathlib import Path

AUTH_FILE = Path(__file__).parent / "data" / ".auth"


def _generate_password() -> str:
    return secrets.token_urlsafe(18)


def _store_password(password: str):
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUTH_FILE.write_text(password)
    os.chmod(AUTH_FILE, 0o600)


def get_or_create_password() -> str:
    """Priority: CALLO_PASSWORD env var (always wins, and updates the stored
    copy) > previously stored password > a freshly generated one, printed
    once and saved to a 0600 file so restarts don't change it."""
    env_password = os.environ.get("CALLO_PASSWORD")
    if env_password:
        _store_password(env_password)
        return env_password

    if AUTH_FILE.exists():
        return AUTH_FILE.read_text().strip()

    password = _generate_password()
    _store_password(password)
    return password


def check_password(candidate: str, actual: str) -> bool:
    return hmac.compare_digest((candidate or "").encode(), actual.encode())
