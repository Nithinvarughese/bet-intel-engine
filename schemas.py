from pydantic import BaseModel
from datetime import datetime

from typing import Optional

# Explicitly export MatchSchema for import in other modules
__all__ = ["MatchSchema"]

class MatchSchema(BaseModel):
    id: int
    league_id: Optional[int] = None
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    status: str
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None

    class Config:
        from_attributes = True # This allows Pydantic to talk to SQLAlchemy