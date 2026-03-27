import pandas as pd
from database import engine
from scipy.stats import poisson

def get_league_averages():
    # 1. Pull your data into a Pandas DataFrame (The Data Scientist's best friend)
    df = pd.read_sql("SELECT * FROM matches WHERE status = 'FT'", engine)
    
    # 2. Calculate League Averages
    avg_home_goals = df['home_goals'].mean()
    avg_away_goals = df['away_goals'].mean()
    
    # 3. Calculate Team Strengths
    # How much BETTER is a team than the average?
    home_attack = df.groupby('home_team')['home_goals'].mean() / avg_home_goals
    away_defense = df.groupby('home_team')['away_goals'].mean() / avg_away_goals
    
    return avg_home_goals, avg_away_goals, home_attack, away_defense

def predict_match(home_team, away_team, avg_h, avg_a, h_att, h_def, a_att, a_def):
    # 1. Calculate the 'Expected Goals' (ExpG) for this specific matchup
    # Note: We need 'Home Defense' and 'Away Attack' which we'll add to our get_averages
    
    exp_home_goals = h_att[home_team] * a_def[away_team] * avg_h
    exp_away_goals = a_att[away_team] * h_def[home_team] * avg_a
    
    # 2. Create a 6x6 grid of possible scorelines (0-5 goals each)
    home_probs = [poisson.pmf(i, exp_home_goals) for i in range(6)]
    away_probs = [poisson.pmf(i, exp_away_goals) for i in range(6)]
    
    # 3. Calculate Win/Draw/Loss probabilities
    home_win = 0
    draw = 0
    away_win = 0
    
    score_matrix = [[0]*6 for _ in range(6)]
    btts_prob = 0
    over_25 = 0
    under_25 = 0
    
    for h in range(6):
        for a in range(6):
            prob = home_probs[h] * away_probs[a]
            score_matrix[h][a] = prob
            
            if h > a: home_win += prob
            elif h == a: draw += prob
            else: away_win += prob
            
            if h > 0 and a > 0: btts_prob += prob
            if h + a > 2.5: over_25 += prob
            else: under_25 += prob
            
    return {
        "h_win": home_win,
        "draw": draw,
        "a_win": away_win,
        "btts": btts_prob,
        "over_25": over_25,
        "under_25": under_25,
        "score_matrix": score_matrix,
        "exp_home": exp_home_goals,
        "exp_away": exp_away_goals
    }

def get_team_form(team_name, limit=5):
    query = f"""
    SELECT match_date, home_team, away_team, home_goals, away_goals 
    FROM matches 
    WHERE (home_team = '{team_name}' OR away_team = '{team_name}')
    AND status = 'FT'
    ORDER BY match_date DESC
    LIMIT {limit}
    """
    df = pd.read_sql(query, engine)
    
    form = []
    for _, row in df.iterrows():
        if row['home_team'] == team_name:
            if row['home_goals'] > row['away_goals']: form.append('W')
            elif row['home_goals'] == row['away_goals']: form.append('D')
            else: form.append('L')
        else:
            if row['away_goals'] > row['home_goals']: form.append('W')
            elif row['away_goals'] == row['home_goals']: form.append('D')
            else: form.append('L')
    return form

def get_h2h_matches(team_a, team_b, limit=5):
    query = f"""
    SELECT match_date, home_team, away_team, home_goals, away_goals 
    FROM matches 
    WHERE ((home_team = '{team_a}' AND away_team = '{team_b}') 
       OR (home_team = '{team_b}' AND away_team = '{team_a}'))
    AND status = 'FT'
    ORDER BY match_date DESC
    LIMIT {limit}
    """
    return pd.read_sql(query, engine)

# --- Updated get_league_averages to include all 4 metrics ---
def get_league_averages_full():
    df = pd.read_sql("SELECT * FROM matches WHERE status = 'FT'", engine)
    avg_h, avg_a = df['home_goals'].mean(), df['away_goals'].mean()
    
    # Attack/Defense Strengths for Home and Away
    h_att = df.groupby('home_team')['home_goals'].mean() / avg_h
    h_def = df.groupby('home_team')['away_goals'].mean() / avg_a
    a_att = df.groupby('away_team')['away_goals'].mean() / avg_a
    a_def = df.groupby('away_team')['home_goals'].mean() / avg_h
    
    return avg_h, avg_a, h_att, h_def, a_att, a_def

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        avg_h, avg_a, h_att, a_def = get_league_averages()
        print(f"League avg home goals: {avg_h:.2f}")
        print("\nTop 5 home attacks (strength index):")
        print(h_att.sort_values(ascending=False).head(5))
    else:
        avg_h, avg_a, h_att, h_def, a_att, a_def = get_league_averages_full()
        preds = predict_match("Arsenal", "Chelsea", avg_h, avg_a, h_att, h_def, a_att, a_def)
        print("\nSample prediction: Arsenal vs Chelsea")
        print(f"  Home win: {preds['h_win']:.2%}")
        print(f"  Draw: {preds['draw']:.2%}")
        print(f"  Away win: {preds['a_win']:.2%}")
        print("\n(Run with `python analytics.py summary` for league averages snippet.)")