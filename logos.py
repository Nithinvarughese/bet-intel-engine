"""Team / league images from API-Sports CDN (GET returns 200; HEAD may 403 — fetch with requests)."""

from __future__ import annotations

from urllib.parse import quote_plus

import requests
from sqlalchemy import text

import pandas as pd

from database import get_engine


def league_logo_url(league_id: int) -> str:
    return f"https://media.api-sports.io/football/leagues/{league_id}.png"


def team_logo_url(team_id: int) -> str:
    return f"https://media.api-sports.io/football/teams/{team_id}.png"


def fallback_avatar_url(team_name: str) -> str:
    """Always-loadable placeholder (initials) when CDN or DB ids are missing."""
    name = (team_name or "Team").strip()[:40]
    return (
        "https://ui-avatars.com/api/?"
        f"name={quote_plus(name)}&size=256&background=0f172a&color=38bdf8&bold=true"
    )


def fetch_image_bytes(url: str, timeout: float = 25.0) -> bytes | None:
    try:
        r = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "PitchMetrics/1.0 (Streamlit)"},
        )
        if r.status_code == 200 and len(r.content) > 100:
            return r.content
    except Exception:
        pass
    return None


def fetch_team_logo_png(team_id: int) -> bytes | None:
    return fetch_image_bytes(team_logo_url(team_id))


def fetch_league_logo_png(league_id: int) -> bytes | None:
    return fetch_image_bytes(league_logo_url(league_id))


def build_team_logo_map(league_id: int) -> dict[str, int]:
    """
    Map team display name -> API team id for one league (from ingested matches).
    """
    q = text(
        """
        SELECT home_team AS name, home_team_id AS tid FROM matches
        WHERE league_id = :lid AND home_team_id IS NOT NULL
        UNION
        SELECT away_team, away_team_id FROM matches
        WHERE league_id = :lid AND away_team_id IS NOT NULL
        """
    )
    try:
        df = pd.read_sql(q, get_engine(), params={"lid": league_id})
    except Exception:
        return {}
    if df.empty:
        return {}
    df.columns = [str(c).lower() for c in df.columns]
    if "name" not in df.columns or "tid" not in df.columns:
        return {}
    df = df.dropna(subset=["tid"])
    out: dict[str, int] = {}
    for _, row in df.iterrows():
        try:
            tid = int(row["tid"])
        except (TypeError, ValueError):
            continue
        name = str(row["name"]).strip()
        if name:
            out[name] = tid
    return out


def resolve_team_id(team_name: str, logo_map: dict[str, int]) -> int | None:
    if not team_name:
        return None
    name = team_name.strip()
    if name in logo_map:
        return logo_map[name]
    name_lower = name.lower()
    for k, v in logo_map.items():
        if k.lower() == name_lower:
            return v
    return None
