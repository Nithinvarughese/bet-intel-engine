import numpy as np
import pandas as pd
from sqlalchemy import text

from database import engine
from scipy.stats import poisson


def get_league_averages():
    df = pd.read_sql(text("SELECT * FROM matches WHERE status = 'FT'"), engine)

    avg_home_goals = df["home_goals"].mean()
    avg_away_goals = df["away_goals"].mean()

    home_attack = df.groupby("home_team")["home_goals"].mean() / avg_home_goals
    away_defense = df.groupby("home_team")["away_goals"].mean() / avg_away_goals

    return avg_home_goals, avg_away_goals, home_attack, away_defense


def predict_match(home_team, away_team, avg_h, avg_a, h_att, h_def, a_att, a_def):
    exp_home_goals = h_att[home_team] * a_def[away_team] * avg_h
    exp_away_goals = a_att[away_team] * h_def[home_team] * avg_a

    home_probs = [poisson.pmf(i, exp_home_goals) for i in range(6)]
    away_probs = [poisson.pmf(i, exp_away_goals) for i in range(6)]

    home_win = 0
    draw = 0
    away_win = 0

    score_matrix = [[0] * 6 for _ in range(6)]
    btts_prob = 0
    over_25 = 0
    under_25 = 0

    for h in range(6):
        for a in range(6):
            prob = home_probs[h] * away_probs[a]
            score_matrix[h][a] = prob

            if h > a:
                home_win += prob
            elif h == a:
                draw += prob
            else:
                away_win += prob

            if h > 0 and a > 0:
                btts_prob += prob
            if h + a > 2.5:
                over_25 += prob
            else:
                under_25 += prob

    return {
        "h_win": home_win,
        "draw": draw,
        "a_win": away_win,
        "btts": btts_prob,
        "over_25": over_25,
        "under_25": under_25,
        "score_matrix": score_matrix,
        "exp_home": exp_home_goals,
        "exp_away": exp_away_goals,
    }


def get_team_form(team_name: str, league_id: int, limit: int = 5):
    q = text(
        """
        SELECT match_date, home_team, away_team, home_goals, away_goals
        FROM matches
        WHERE (home_team = :team OR away_team = :team)
          AND status = 'FT'
          AND league_id = :league_id
        ORDER BY match_date DESC
        LIMIT :limit
        """
    )
    df = pd.read_sql(
        q, engine, params={"team": team_name, "league_id": league_id, "limit": limit}
    )

    form = []
    for _, row in df.iterrows():
        if row["home_team"] == team_name:
            if row["home_goals"] > row["away_goals"]:
                form.append("W")
            elif row["home_goals"] == row["away_goals"]:
                form.append("D")
            else:
                form.append("L")
        else:
            if row["away_goals"] > row["home_goals"]:
                form.append("W")
            elif row["away_goals"] == row["home_goals"]:
                form.append("D")
            else:
                form.append("L")
    return form


def get_h2h_matches(team_a: str, team_b: str, league_id: int, limit: int = 5):
    q = text(
        """
        SELECT match_date, home_team, away_team, home_goals, away_goals
        FROM matches
        WHERE (
            (home_team = :a AND away_team = :b)
            OR (home_team = :b AND away_team = :a)
        )
        AND status = 'FT'
        AND league_id = :league_id
        ORDER BY match_date DESC
        LIMIT :limit
        """
    )
    return pd.read_sql(
        q,
        engine,
        params={"a": team_a, "b": team_b, "league_id": league_id, "limit": limit},
    )


def get_league_averages_full(league_id: int = 39):
    q = text(
        """
        SELECT * FROM matches
        WHERE status = 'FT' AND league_id = :league_id
        """
    )
    df = pd.read_sql(q, engine, params={"league_id": league_id})

    if df.empty:
        empty_series = pd.Series(dtype=float)
        return 0.0, 0.0, empty_series, empty_series, empty_series, empty_series

    # Calculate Time Decay Factors (Recency Bias)
    # Matches that happened closer to the latest match receive higher weight.
    df['match_date'] = pd.to_datetime(df['match_date'])
    max_date = df['match_date'].max()
    df['days_ago'] = (max_date - df['match_date']).dt.days
    
    # Exponential decay: e.g., halving roughly every 60 days
    df['weight'] = np.exp(-df['days_ago'] / 90.0)

    # Weighted league averages
    total_weight = df['weight'].sum()
    if total_weight == 0:
        total_weight = 1.0  # fallback
        
    avg_h = (df["home_goals"] * df["weight"]).sum() / total_weight
    avg_a = (df["away_goals"] * df["weight"]).sum() / total_weight

    def weighted_mean(group, col):
        w_sum = group['weight'].sum()
        if w_sum == 0: return 0.0
        return (group[col] * group['weight']).sum() / w_sum

    h_att = df.groupby("home_team").apply(lambda x: weighted_mean(x, "home_goals")) / avg_h
    h_def = df.groupby("home_team").apply(lambda x: weighted_mean(x, "away_goals")) / avg_a
    a_att = df.groupby("away_team").apply(lambda x: weighted_mean(x, "away_goals")) / avg_a
    a_def = df.groupby("away_team").apply(lambda x: weighted_mean(x, "home_goals")) / avg_h

    return avg_h, avg_a, h_att, h_def, a_att, a_def


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        avg_h, avg_a, h_att, a_def = get_league_averages()
        print(f"League avg home goals: {avg_h:.2f}")
        print("\nTop 5 home attacks (strength index):")
        print(h_att.sort_values(ascending=False).head(5))
    else:
        avg_h, avg_a, h_att, h_def, a_att, a_def = get_league_averages_full(39)
        preds = predict_match("Arsenal", "Chelsea", avg_h, avg_a, h_att, h_def, a_att, a_def)
        print("\nSample prediction: Arsenal vs Chelsea (league_id=39)")
        print(f"  Home win: {preds['h_win']:.2%}")
        print(f"  Draw: {preds['draw']:.2%}")
        print(f"  Away win: {preds['a_win']:.2%}")
        print("\n(Run with `python analytics.py summary` for all-league averages snippet.)")
