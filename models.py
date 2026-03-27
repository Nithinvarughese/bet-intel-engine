from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


# This is the "Base" that all our tables will grow from
Base = declarative_base()

# Explicitly export Base and MatchModel for import in other modules
__all__ = ["Base", "MatchModel"]

class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True) # The API's Match ID
    league_id = Column(Integer, nullable=True, index=True)
    league_name = Column(String)
    match_date = Column(DateTime)
    home_team = Column(String)
    away_team = Column(String)
    home_team_id = Column(Integer, nullable=True, index=True)
    away_team_id = Column(Integer, nullable=True, index=True)
    home_goals = Column(Integer, nullable=True) # Nullable because it hasn't happened yet!
    away_goals = Column(Integer, nullable=True)
    status = Column(String) # 'NS' for Not Started, 'FT' for Finished