import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env and add your PostgreSQL URL."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
print("🚀 Tables created successfully in the database!")
