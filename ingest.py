import os
import requests
from dotenv import load_dotenv
from database import SessionLocal, engine
import models
from schemas import MatchSchema
from models import MatchModel

# 1. Initialize Tables (NV - Ensure DB is ready)
models.Base.metadata.create_all(bind=engine)

load_dotenv()
API_KEY = os.getenv("FOOTBALL_API_KEY")

# USE THE HEADERS THAT WORKED IN YOUR TEST SCRIPT
HEADERS = {
    'x-apisports-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io"
}

def fetch_and_save_matches(league_id: int = 39, season: int = 2023):
    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"
    
    print(f"📡 Fetching data from: {url}")
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    # DEBUG: Let's see what the API actually said
    if data.get("errors"):
        print(f"❌ API Errors: {data['errors']}")
        return

    if not data.get("response"):
        print(f"⚠️ No matches found. Raw Response: {data}")
        return

    db = SessionLocal()
    try:
        for item in data['response']:
            # Validate with Schema
            match_data = MatchSchema(
                id=item['fixture']['id'],
                league_name=item['league']['name'],
                match_date=item['fixture']['date'],
                home_team=item['teams']['home']['name'],
                away_team=item['teams']['away']['name'],
                status=item['fixture']['status']['short'],
                home_goals=item['goals']['home'],
                away_goals=item['goals']['away']
            )

            # Upsert Logic (Check if exists)
            existing = db.query(MatchModel).filter(MatchModel.id == match_data.id).first()
            if not existing:
                new_row = MatchModel(**match_data.dict())
                db.add(new_row)
                print(f"✅ Saved: {match_data.home_team} vs {match_data.away_team}")
        
        db.commit()
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fetch_and_save_matches()