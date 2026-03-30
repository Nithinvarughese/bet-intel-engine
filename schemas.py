from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

__all__ = ["MatchSchema"]


@dataclass
class MatchSchema:
    id: int
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str
    league_id: Optional[int] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None

    def model_dump(self) -> dict:
        return asdict(self)
