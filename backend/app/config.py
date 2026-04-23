"""Load config from environment (.env). No hardcoded store name or currency."""
import os
from pathlib import Path
from urllib.parse import unquote

from dotenv import load_dotenv

# Load .env from backend/ (same directory as this package's parent)
_backend_dir = Path(__file__).resolve().parent.parent
_env_path = _backend_dir / ".env"
load_dotenv(_env_path)

_instance_dir = _backend_dir / "instance"
_default_sqlite_file = (_instance_dir / "iwear_dev.db").resolve()


def _sqlite_creator(db_path: Path):
    """Return a no-arg callable for SQLAlchemy ``creator=`` (paths with spaces work on Windows)."""

    def connect():
        import sqlite3

        # Flask dev server is multi-threaded; SQLite defaults to same-thread only.
        return sqlite3.connect(
            str(db_path.resolve()),
            check_same_thread=False,
        )

    return connect


def _sqlite_uri_and_engine_options():
    """
    Build SQLALCHEMY_DATABASE_URI and optional SQLALCHEMY_ENGINE_OPTIONS.

    For file-based SQLite we use a ``creator`` that passes a plain path string to
    sqlite3. URLs like ``sqlite:///C:/folder%20name/db.sqlite`` often break on
    Windows because the driver does not open the file the same way as a direct path.
    """
    raw = os.environ.get("DATABASE_URL")
    if not raw:
        _instance_dir.mkdir(parents=True, exist_ok=True)
        return "sqlite://", {"creator": _sqlite_creator(_default_sqlite_file)}

    if not raw.startswith("sqlite"):
        return raw, {}

    from sqlalchemy.engine.url import make_url

    u = make_url(raw)
    db = u.database
    if db in (None, ":memory:") or (isinstance(db, str) and db.startswith(":memory")):
        return raw, {}

    path_str = unquote(db)
    p = Path(path_str)
    if not p.is_absolute():
        p = (_backend_dir / p).resolve()
    else:
        p = p.resolve()

    _instance_dir.mkdir(parents=True, exist_ok=True)
    return "sqlite://", {"creator": _sqlite_creator(p)}


_uri, _opts = _sqlite_uri_and_engine_options()


class Config:
    """Base config from env vars. Store branding/currency come from store_settings (DB)."""

    # JWT needs at least 32 bytes for SHA256; default is 32 chars
    _default_secret = "dev-secret-change-in-production-32b"
    SECRET_KEY = os.environ.get("SECRET_KEY", _default_secret)
    SQLALCHEMY_DATABASE_URI = _uri
    SQLALCHEMY_ENGINE_OPTIONS = _opts
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", os.environ.get("SECRET_KEY", _default_secret))
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", "86400"))  # 24h default
