import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. For local dev: copy `.env.example` to `.env`. "
        "For Streamlit Cloud: set DATABASE_URL in App secrets (see `.streamlit/secrets.toml.example`)."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_league_id_column():
    """Add league_id to matches if missing (existing DBs created before multi-league support)."""
    try:
        insp = inspect(engine)
        if "matches" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("matches")}
        if "league_id" in cols:
            return
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE matches ADD COLUMN league_id INTEGER"))
    except Exception:
        pass


ensure_league_id_column()


def backfill_league_ids_from_names():
    """Set league_id on legacy rows where it is NULL (name must match API `league.name`)."""
    variants = {
        39: ("Premier League",),
        140: ("La Liga", "Primera División", "Primera Division"),
        135: ("Serie A",),
        78: ("Bundesliga",),
        61: ("Ligue 1",),
    }
    try:
        insp = inspect(engine)
        if "matches" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("matches")}
        if "league_id" not in cols:
            return
        with engine.begin() as conn:
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


backfill_league_ids_from_names()


def ensure_team_id_columns():
    """Add home_team_id / away_team_id for API-Sports logo CDN URLs."""
    try:
        insp = inspect(engine)
        if "matches" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("matches")}
        with engine.begin() as conn:
            if "home_team_id" not in cols:
                conn.execute(text("ALTER TABLE matches ADD COLUMN home_team_id INTEGER"))
            if "away_team_id" not in cols:
                conn.execute(text("ALTER TABLE matches ADD COLUMN away_team_id INTEGER"))
    except Exception:
        pass


ensure_team_id_columns()


def test_connection():
    try:
        connection = engine.connect()
        print("✅ Success! Python is officially talking to the Database.")
        connection.close()
    except Exception as e:
        print(f"❌ Error: Could not connect. {e}")


if __name__ == "__main__":
    test_connection()

from models import Base
import models

Base.metadata.create_all(bind=engine)
