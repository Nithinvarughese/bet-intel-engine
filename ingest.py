import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load env before reading API keys or importing DB (so FOOTBALL_API_KEY is available)
load_dotenv(Path(__file__).resolve().parent / ".env")

import requests
from database import SessionLocal, engine
import models
from schemas import MatchSchema
from models import MatchModel

models.Base.metadata.create_all(bind=engine)


def api_headers():
    """
    API-Sports keys from https://dashboard.api-football.com use x-apisports-key.
    RapidAPI subscriptions use X-RapidAPI-Key + X-RapidAPI-Host instead.
    """
    direct = (os.getenv("FOOTBALL_API_KEY") or os.getenv("APISPORTS_KEY") or "").strip()
    rapid = (os.getenv("RAPIDAPI_KEY") or "").strip()
    if rapid:
        return {
            "X-RapidAPI-Key": rapid,
            "X-RapidAPI-Host": "v3.football.api-sports.io",
        }
    if direct:
        return {"x-apisports-key": direct}
    return None


def _schema_payload(match_data: MatchSchema) -> dict:
    if hasattr(match_data, "model_dump"):
        return match_data.model_dump()
    return match_data.dict()


def fetch_and_save_matches(league_id: int = 39, season: int = 2023):
    headers = api_headers()
    if not headers:
        print(
            "❌ No API key found. Add one of these to your `.env` file:\n"
            "   FOOTBALL_API_KEY=<key>     # from https://dashboard.api-football.com\n"
            "   RAPIDAPI_KEY=<key>         # if you subscribed via RapidAPI\n"
        )
        return

    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"

    print(f"📡 Fetching data from: {url}")
    response = requests.get(url, headers=headers, timeout=60)
    data = response.json()

    if data.get("errors"):
        print(f"❌ API Errors: {data['errors']}")
        return

    if not data.get("response"):
        print(f"⚠️ No matches found. Raw Response: {data}")
        return

    db = SessionLocal()
    try:
        for item in data["response"]:
            league = item["league"]
            match_data = MatchSchema(
                id=item["fixture"]["id"],
                league_id=league["id"],
                league_name=league["name"],
                match_date=item["fixture"]["date"],
                home_team=item["teams"]["home"]["name"],
                away_team=item["teams"]["away"]["name"],
                home_team_id=item["teams"]["home"]["id"],
                away_team_id=item["teams"]["away"]["id"],
                status=item["fixture"]["status"]["short"],
                home_goals=item["goals"]["home"],
                away_goals=item["goals"]["away"],
            )

            payload = _schema_payload(match_data)
            existing = db.query(MatchModel).filter(MatchModel.id == match_data.id).first()
            if existing:
                for key, value in payload.items():
                    setattr(existing, key, value)
            else:
                db.add(MatchModel(**payload))
                print(f"✅ Saved: {match_data.home_team} vs {match_data.away_team}")

        db.commit()
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if not api_headers():
        print(
            "❌ Missing API key. Create `.env` in the project root with:\n\n"
            "   FOOTBALL_API_KEY=paste_your_key_here\n\n"
            "Get a key: https://dashboard.api-football.com (free tier available).\n"
            "If you use RapidAPI instead, set RAPIDAPI_KEY=...\n"
        )
        sys.exit(1)

    LEAGUES_TO_FETCH = [39, 140, 135, 78, 61]
    for lid in LEAGUES_TO_FETCH:
        print(f"\n--- Fetching League ID {lid} ---")
        fetch_and_save_matches(league_id=lid, season=2023)
    print("\n🎉 All leagues synced to PostgreSQL (league_id stored on each row).")
