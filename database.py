import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).resolve().parent / ".env")

from models import Base
import models  # noqa: F401 — registers MatchModel on Base.metadata

_engine = None
_SessionLocal = None

# Env keys some hosts / docs use instead of DATABASE_URL
_ENV_URL_KEYS = (
    "DATABASE_URL",
    "POSTGRES_URL",
    "SQLALCHEMY_DATABASE_URI",
    "PGURL",
    "NEON_DATABASE_URL",
)


def _looks_like_postgres_url(v: str) -> bool:
    x = (v or "").strip().lower()
    return x.startswith(("postgresql://", "postgres://", "postgresql+"))


def _first_env_database_url() -> str | None:
    for key in _ENV_URL_KEYS:
        v = (os.environ.get(key) or "").strip()
        if v and _looks_like_postgres_url(v):
            return v
    return None


def _walk_secret_values(obj, depth: int = 0):
    """Yield string leaves from nested TOML (Streamlit sections, lists, etc.)."""
    if depth > 14:
        return
    if isinstance(obj, str):
        yield obj
        return
    if isinstance(obj, (int, float, bool)) or obj is None:
        return
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_secret_values(v, depth + 1)
        return
    if isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _walk_secret_values(v, depth + 1)
        return
    if hasattr(obj, "keys") and callable(obj.keys) and hasattr(obj, "__getitem__"):
        try:
            for k in obj.keys():
                try:
                    yield from _walk_secret_values(obj[k], depth + 1)
                except (KeyError, TypeError):
                    continue
        except Exception:
            return


def _database_url_from_streamlit_secrets() -> str | None:
    """Cloud UI secrets are TOML: root keys often mirror env; nested sections only live under st.secrets."""
    try:
        import streamlit as st
    except ImportError:
        return None
    try:
        sec = st.secrets
    except Exception:
        return None

    # Explicit keys / nested shapes users often paste from provider docs
    _candidates = (
        ("DATABASE_URL",),
        ("database_url",),
        ("database", "url"),
        ("db", "url"),
        ("postgres", "url"),
        ("connections", "postgresql", "url"),
        ("connections", "postgresql", "database_url"),
    )
    for path in _candidates:
        try:
            cur = sec
            for p in path:
                cur = cur[p]
            s = str(cur).strip()
            if _looks_like_postgres_url(s):
                return s
        except (KeyError, TypeError):
            continue

    for s in _walk_secret_values(sec):
        t = (s or "").strip()
        if _looks_like_postgres_url(t):
            return t
    return None


def _resolve_database_url() -> str:
    """`.env` / OS env first, then Streamlit secrets (any nesting that contains a postgres URL)."""
    u = _first_env_database_url()
    if u:
        os.environ.setdefault("DATABASE_URL", u)
        return u

    u = _database_url_from_streamlit_secrets()
    if u:
        os.environ["DATABASE_URL"] = u
        return u

    raise RuntimeError(
        "No PostgreSQL URL found. Local: set DATABASE_URL in `.env`. "
        "Streamlit Cloud: App settings → Secrets → TOML with a root line like "
        '`DATABASE_URL = "postgresql://..."` '
        "or nest under `[database]` as `url = \"postgresql://...\"` "
        "(see `.streamlit/secrets.toml.example`)."
    )


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(_resolve_database_url())
        ensure_league_id_column()
        backfill_league_ids_from_names()
        ensure_team_id_columns()
        Base.metadata.create_all(bind=_engine)
    return _engine


def get_engine():
    """Shared SQLAlchemy engine; lazy so Streamlit Cloud can read `st.secrets` after imports finish."""
    return _get_engine()


def __getattr__(name: str):
    if name == "engine":
        return _get_engine()
    if name == "SessionLocal":
        global _SessionLocal
        if _SessionLocal is None:
            _SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=_get_engine()
            )
        return _SessionLocal
    if name == "DATABASE_URL":
        return _resolve_database_url()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def ensure_league_id_column():
    """Add league_id to matches if missing (existing DBs created before multi-league support)."""
    eng = _get_engine()
    try:
        insp = inspect(eng)
        if "matches" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("matches")}
        if "league_id" in cols:
            return
        with eng.begin() as conn:
            conn.execute(text("ALTER TABLE matches ADD COLUMN league_id INTEGER"))
    except Exception:
        pass


def backfill_league_ids_from_names():
    """Set league_id on legacy rows where it is NULL (name must match API `league.name`)."""
    eng = _get_engine()
    variants = {
        39: ("Premier League",),
        140: ("La Liga", "Primera División", "Primera Division"),
        135: ("Serie A",),
        78: ("Bundesliga",),
        61: ("Ligue 1",),
    }
    try:
        insp = inspect(eng)
        if "matches" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("matches")}
        if "league_id" not in cols:
            return
        with eng.begin() as conn:
            for lid, names in variants.items():
                for name in names:
                    conn.execute(
                        text(
                            "UPDATE matches SET league_id = :lid "
                            "WHERE league_id IS NULL AND league_name = :n"
                        ),
                        {"lid": lid, "n": name},
                    )
    except Exception:
        pass


def ensure_team_id_columns():
    """Add home_team_id / away_team_id for API-Sports logo CDN URLs."""
    eng = _get_engine()
    try:
        insp = inspect(eng)
        if "matches" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("matches")}
        with eng.begin() as conn:
            if "home_team_id" not in cols:
                conn.execute(text("ALTER TABLE matches ADD COLUMN home_team_id INTEGER"))
            if "away_team_id" not in cols:
                conn.execute(text("ALTER TABLE matches ADD COLUMN away_team_id INTEGER"))
    except Exception:
        pass


def test_connection():
    try:
        connection = _get_engine().connect()
        print("✅ Success! Python is officially talking to the Database.")
        connection.close()
    except Exception as e:
        print(f"❌ Error: Could not connect. {e}")


if __name__ == "__main__":
    test_connection()
