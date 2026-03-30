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


def _resolve_database_url() -> str:
    """Prefer `.env` / OS env; on Streamlit Cloud, `st.secrets` is ready only after import (lazy access)."""
    u = (os.environ.get("DATABASE_URL") or "").strip()
    if u:
        return u
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
            s = str(st.secrets["DATABASE_URL"]).strip()
            if s:
                os.environ["DATABASE_URL"] = s
                return s
    except Exception:
        pass
    raise RuntimeError(
        "DATABASE_URL is not set. For local dev: copy `.env.example` to `.env`. "
        "For Streamlit Cloud: set DATABASE_URL in App secrets (see `.streamlit/secrets.toml.example`)."
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
