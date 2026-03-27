import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import get_league_averages_full, predict_match, get_team_form, get_h2h_matches

st.set_page_config(
    page_title="Bet Intel | Football analytics demo",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEAM_LOGOS = {
    "Arsenal": "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png",
    "Aston Villa": "https://r2.thesportsdb.com/images/media/team/badge/jykrpv1717309891.png",
    "Bournemouth": "https://r2.thesportsdb.com/images/media/team/badge/y08nak1534071116.png",
    "Brentford": "https://r2.thesportsdb.com/images/media/team/badge/grv1aw1546453779.png",
    "Brighton": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fd/Brighton_%26_Hove_Albion_logo.svg/1024px-Brighton_%26_Hove_Albion_logo.svg.png",
    "Burnley": "https://r2.thesportsdb.com/images/media/team/badge/ql7nl31686893820.png",
    "Chelsea": "https://r2.thesportsdb.com/images/media/team/badge/yvwvtu1448813215.png",
    "Crystal Palace": "https://r2.thesportsdb.com/images/media/team/badge/ia6i3m1656014992.png",
    "Everton": "https://r2.thesportsdb.com/images/media/team/badge/eqayrf1523184794.png",
    "Fulham": "https://r2.thesportsdb.com/images/media/team/badge/xwwvyt1448811086.png",
    "Liverpool": "https://r2.thesportsdb.com/images/media/team/badge/kfaher1737969724.png",
    "Luton": "https://r2.thesportsdb.com/images/media/team/badge/v977eh1681319466.png",
    "Manchester City": "https://r2.thesportsdb.com/images/media/team/badge/vwpvry1467462651.png",
    "Manchester United": "https://r2.thesportsdb.com/images/media/team/badge/xzqdr11517660252.png",
    "Newcastle": "https://r2.thesportsdb.com/images/media/team/badge/aes2o51646347790.png",
    "Nottingham Forest": "https://r2.thesportsdb.com/images/media/team/badge/bk4qjs1546440351.png",
    "Sheffield Utd": "https://r2.thesportsdb.com/images/media/team/badge/w7f8pj1672950689.png",
    "Tottenham": "https://r2.thesportsdb.com/images/media/team/badge/dfyfhl1604094109.png",
    "West Ham": "https://r2.thesportsdb.com/images/media/team/badge/yutyxs1467459956.png",
    "Wolves": "https://r2.thesportsdb.com/images/media/team/badge/saimjk1656789616.png"
}

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;700;900&display=swap');

    /* Font Overrides */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6, .team-name, .prob-val, .main-title {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Premium Background Overlay */
    [data-testid="stAppViewContainer"] {
        background-color: #0b1120;
        background-image: 
            radial-gradient(at 0% 0%, rgba(15, 23, 42, 1) 0, transparent 50%),
            radial-gradient(at 50% 100%, rgba(15, 23, 42, 1) 0, transparent 50%),
            radial-gradient(at 100% 0%, rgba(56, 189, 248, 0.08) 0, transparent 50%);
        background-attachment: fixed;
    }

    /* Entrance Animation */
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stAppViewBlockContainer"] {
        animation: slideDown 0.8s ease-out forwards;
    }
    
    .team-logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        height: 120px;
        filter: drop-shadow(0px 10px 15px rgba(0, 0, 0, 0.5));
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), filter 0.4s ease;
    }
    .team-logo:hover {
        transform: scale(1.15) translateY(-5px);
        filter: drop-shadow(0px 15px 25px rgba(56, 189, 248, 0.4));
    }
    .team-name {
        text-align: center;
        font-size: 26px;
        font-weight: 700;
        margin-top: 15px;
        color: #f8fafc;
        text-shadow: 1px 2px 4px rgba(0,0,0,0.5);
    }
    .prob-val {
        text-align: center;
        font-size: 56px;
        font-weight: 900;
        margin-top: -15px;
        letter-spacing: -2px;
    }
    .prob-home { color: #38bdf8; text-shadow: 0 0 25px rgba(56,189,248,0.5); }
    .prob-draw { color: #94a3b8; font-size: 38px; padding-top: 12px; text-shadow: 0 0 15px rgba(148,163,184,0.3); }
    .prob-away { color: #a78bfa; text-shadow: 0 0 25px rgba(167,139,250,0.5); }
    
    .prob-label {
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-size: 13px;
        color: #64748b;
        margin-top: -10px;
        margin-bottom: 20px;
        font-weight: 600;
    }
    .match-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border-radius: 24px;
        padding: 40px 24px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        margin-top: 20px;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.08);
        color: white;
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
    }
    .match-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(56,189,248,0.3), transparent);
    }
    .main-title {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #f8fafc, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 4.5rem;
        letter-spacing: -2px;
        margin-bottom: 5px;
        text-transform: uppercase;
        filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.4));
    }
    .sub-title {
        text-align: center;
        color: #38bdf8;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 40px;
        text-transform: uppercase;
        letter-spacing: 4px;
        opacity: 0.9;
    }
    .form-badge {
        display: inline-block;
        width: 24px;
        height: 24px;
        border-radius: 6px;
        color: white;
        font-size: 12px;
        font-weight: 800;
        line-height: 24px;
        text-align: center;
        margin: 0 4px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .form-W { background: linear-gradient(135deg, #10b981 0%, #047857 100%); }
    .form-D { background: linear-gradient(135deg, #64748b 0%, #334155 100%); }
    .form-L { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data(ttl=3600, show_spinner="Loading league statistics…")
def load_league():
    return get_league_averages_full()


def team_index(teams: list, name: str, fallback: int = 0) -> int:
    try:
        return teams.index(name)
    except ValueError:
        return fallback

def score_heatmap(score_matrix, home, away):
    fig = px.imshow(score_matrix, 
                    labels=dict(x=f"{away} Goals", y=f"{home} Goals", color="Probability"),
                    x=[str(i) for i in range(6)], y=[str(i) for i in range(6)],
                    color_continuous_scale="Teal", text_auto=".1%")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        height=380, margin=dict(t=20, b=20, l=20, r=20)
    )
    fig.update_xaxes(side="top")
    return fig


def outcome_donut(h_win: float, draw: float, a_win: float, home: str, away: str) -> go.Figure:
    fig = go.Figure(data=[go.Pie(
        labels=[f"{home}", "Draw", f"{away}"],
        values=[h_win, draw, a_win],
        hole=.65,
        marker=dict(colors=["#22d3ee", "#64748b", "#0ea5e9"], line=dict(color='#0f172a', width=3)),
        textinfo='percent',
        hoverinfo='label+percent',
        textfont=dict(size=18, color="white")
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5, font=dict(color="#cbd5e1", size=14)),
        margin=dict(t=30, b=30, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350,
        annotations=[dict(text='Probs', x=0.5, y=0.5, font_size=20, showarrow=False, font=dict(color="#94a3b8"))]
    )
    return fig


def power_rankings_figure(power_df: pd.DataFrame) -> go.Figure:
    power_df['Overall Power'] = (power_df['Scoring Power'] + power_df['Defensive Stability']) / 2
    top_10 = power_df.sort_values('Overall Power', ascending=True).tail(10)
    
    fig = go.Figure(go.Bar(
        x=top_10['Overall Power'],
        y=top_10['Team'],
        orientation='h',
        marker=dict(
            color=top_10['Overall Power'],
            colorscale='GnBu',
        ),
        text=top_10['Overall Power'].round(1),
        textposition='inside',
        insidetextfont=dict(color='white')
    ))
    fig.update_layout(
        title=dict(text="League Power Rankings (Top 10)", font=dict(color="#f8fafc", size=22)),
        xaxis=dict(title="Overall Rating (100 = Average)", gridcolor="rgba(51, 65, 85, 0.5)", color="#94a3b8"),
        yaxis=dict(title="", color="#cbd5e1", tickfont=dict(size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=450,
        margin=dict(t=50, b=30, l=20, r=20),
        font=dict(family="system-ui, sans-serif")
    )
    return fig


avg_h, avg_a, h_att, h_def, a_att, a_def = load_league()
teams = sorted(h_att.index.tolist())

if "match_pred" not in st.session_state:
    with st.spinner("Computing default fixture (Arsenal vs Chelsea)…"):
        preds = predict_match("Arsenal", "Chelsea", avg_h, avg_a, h_att, h_def, a_att, a_def)
        preds["home_form"] = get_team_form("Arsenal")
        preds["away_form"] = get_team_form("Chelsea")
        preds["h2h"] = get_h2h_matches("Arsenal", "Chelsea")
    preds["home"] = "Arsenal"
    preds["away"] = "Chelsea"
    st.session_state["match_pred"] = preds

st.markdown('<h1 class="main-title">BET INTEL</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">PREDICTIVE ANALYTICS ENGINE</p>', unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px 30px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 35px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);">
""", unsafe_allow_html=True)

c_home, c_vs, c_away, c_btn = st.columns([3, 1, 3, 2])
with c_home:
    home_team = st.selectbox("Home Team", teams, index=team_index(teams, st.session_state["match_pred"]["home"]), key="sb_home")
with c_vs:
    st.markdown('<div style="text-align:center; font-size: 18px; font-weight:800; margin-top:32px; color:#64748b;">VS</div>', unsafe_allow_html=True)
with c_away:
    away_team = st.selectbox("Away Team", teams, index=team_index(teams, st.session_state["match_pred"]["away"]), key="sb_away")
with c_btn:
    st.markdown('<div style="margin-top:28px;"></div>', unsafe_allow_html=True)
    if st.button("RUN SIMULATION", type="primary", use_container_width=True):
        with st.spinner("Computing match probabilities…"):
            preds = predict_match(home_team, away_team, avg_h, avg_a, h_att, h_def, a_att, a_def)
            preds["home_form"] = get_team_form(home_team)
            preds["away_form"] = get_team_form(away_team)
            preds["h2h"] = get_h2h_matches(home_team, away_team)
        preds["home"] = home_team
        preds["away"] = away_team
        st.session_state["match_pred"] = preds

st.markdown("</div>", unsafe_allow_html=True)

pred = st.session_state["match_pred"]

if home_team != pred["home"] or away_team != pred["away"]:
    st.warning("Selected teams differ from the displayed simulation. Click **RUN SIMULATION** to update.")

st.markdown('<div class="match-card">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    img_url = TEAM_LOGOS.get(pred["home"], "https://upload.wikimedia.org/wikipedia/commons/e/e6/Football_logo.png")
    st.markdown(f'<img src="{img_url}" class="team-logo">', unsafe_allow_html=True)
    st.markdown(f'<div class="team-name">{pred["home"]}</div>', unsafe_allow_html=True)
    form_html = "".join([f'<span class="form-badge form-{res}">{res}</span>' for res in pred["home_form"]])
    st.markdown(f'<div style="text-align:center; margin-bottom:15px;">{form_html}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="prob-val prob-home">{pred["h_win"]:.1%}</div>', unsafe_allow_html=True)
    st.markdown('<div class="prob-label">Win Probability</div>', unsafe_allow_html=True)
    
with c2:
    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="team-name" style="color: #64748b;">DRAW</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 37px;"></div>', unsafe_allow_html=True) # visual spacer matching form badge height
    st.markdown(f'<div class="prob-val prob-draw">{pred["draw"]:.1%}</div>', unsafe_allow_html=True)
    st.markdown('<div class="prob-label">Probability</div>', unsafe_allow_html=True)
    
with c3:
    img_url = TEAM_LOGOS.get(pred["away"], "https://upload.wikimedia.org/wikipedia/commons/e/e6/Football_logo.png")
    st.markdown(f'<img src="{img_url}" class="team-logo">', unsafe_allow_html=True)
    st.markdown(f'<div class="team-name">{pred["away"]}</div>', unsafe_allow_html=True)
    form_html = "".join([f'<span class="form-badge form-{res}">{res}</span>' for res in pred["away_form"]])
    st.markdown(f'<div style="text-align:center; margin-bottom:15px;">{form_html}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="prob-val prob-away">{pred["a_win"]:.1%}</div>', unsafe_allow_html=True)
    st.markdown('<div class="prob-label">Win Probability</div>', unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("🎲 Both Teams To Score (BTTS)", f"{pred['btts']:.1%}")
col_m2.metric("🔥 Over 2.5 Goals", f"{pred['over_25']:.1%}")
col_m3.metric("🧊 Under 2.5 Goals", f"{pred['under_25']:.1%}")

st.markdown("---")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<h3 style="color:#f8fafc; font-weight:700; margin-bottom: 20px;">Match Probability Distribution</h3>', unsafe_allow_html=True)
    st.plotly_chart(
        outcome_donut(pred["h_win"], pred["draw"], pred["a_win"], pred["home"], pred["away"]),
        use_container_width=True,
    )
    
    total_p = pred["h_win"] + pred["draw"] + pred["a_win"]
    st.caption(
        f"**Mathematical Note:** Independent Poisson model grid (capped at 5 goals per side). "
        f"Distribution covers **{total_p:.1%}** of total probability space."
    )
    
    st.markdown('<h3 style="color:#f8fafc; font-weight:700; margin-top: 40px; margin-bottom: 20px;">Correct Score Heatmap</h3>', unsafe_allow_html=True)
    st.plotly_chart(score_heatmap(pred["score_matrix"], pred["home"], pred["away"]), use_container_width=True)

power_df = pd.DataFrame(
    {
        "Team": h_att.index,
        "Scoring Power": (h_att.values * 100).round(1),
        "Defensive Stability": (1 / h_def.values * 100).round(1),
    }
)

with col_right:
    st.plotly_chart(power_rankings_figure(power_df), use_container_width=True)
    
    st.markdown('<h3 style="color:#f8fafc; font-weight:700; margin-top: 20px; margin-bottom: 20px;">Recent Head-to-Head</h3>', unsafe_allow_html=True)
    h2h_df = pred.get("h2h")
    if h2h_df is not None and not h2h_df.empty:
        h2h_display = h2h_df.copy()
        h2h_display['Date'] = pd.to_datetime(h2h_display['match_date'], errors='coerce').dt.strftime('%b %d, %Y')
        h2h_display['Score'] = h2h_display['home_team'] + " " + h2h_display['home_goals'].astype(str) + " - " + h2h_display['away_goals'].astype(str) + " " + h2h_display['away_team']
        st.dataframe(h2h_display[['Date', 'Score']], hide_index=True, use_container_width=True)
    else:
        st.info("No recent head-to-head matches found in database.")

st.markdown("---")

with st.expander("💰 Expected Value (EV) Analyzer", expanded=True):
    st.markdown('<h4 style="color:#f8fafc; font-weight:700; margin-bottom: 10px;">Find Value Bets</h4>', unsafe_allow_html=True)
    st.caption("Enter live bookmaker Decimal Odds below to calculate the Expected Value (EV) over the long run, comparing our model's probability against the bookie's implied probability.")
    
    col_ev1, col_ev2, col_ev3 = st.columns(3)
    with col_ev1:
        h_odds = st.number_input(f"{pred['home']} Win Odds", min_value=1.01, value=2.50, step=0.1, key="odd_h")
        ev_h = (pred['h_win'] * h_odds) - 1
        if ev_h > 0:
            st.success(f"**+EV Found!** ({ev_h:+.1%} ROI)")
        else:
            st.error(f"Negative EV ({ev_h:+.1%} ROI)")
            
    with col_ev2:
        d_odds = st.number_input(f"Draw Odds", min_value=1.01, value=3.20, step=0.1, key="odd_d")
        ev_d = (pred['draw'] * d_odds) - 1
        if ev_d > 0:
            st.success(f"**+EV Found!** ({ev_d:+.1%} ROI)")
        else:
            st.error(f"Negative EV ({ev_d:+.1%} ROI)")
            
    with col_ev3:
        a_odds = st.number_input(f"{pred['away']} Win Odds", min_value=1.01, value=2.80, step=0.1, key="odd_a")
        ev_a = (pred['a_win'] * a_odds) - 1
        if ev_a > 0:
            st.success(f"**+EV Found!** ({ev_a:+.1%} ROI)")
        else:
            st.error(f"Negative EV ({ev_a:+.1%} ROI)")

st.divider()
st.caption("Stack: Streamlit · Plotly · pandas · SciPy (Poisson) · PostgreSQL · SQLAlchemy")
