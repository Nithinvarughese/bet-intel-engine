import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import get_league_averages_full, predict_match

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
    .team-logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        height: 120px;
        filter: drop-shadow(0px 8px 12px rgba(0, 0, 0, 0.4));
        transition: transform 0.3s ease;
    }
    .team-logo:hover {
        transform: scale(1.05);
    }
    .team-name {
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        margin-top: 15px;
        color: #f8fafc;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    .prob-val {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        margin-top: -10px;
        text-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
    .prob-home { color: #22d3ee; }
    .prob-draw { color: #94a3b8; font-size: 32px; padding-top: 10px; }
    .prob-away { color: #0ea5e9; }
    .prob-label {
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 14px;
        color: #94a3b8;
        margin-top: -10px;
        margin-bottom: 20px;
        font-weight: 600;
    }
    .match-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 20px;
        padding: 30px 24px;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
        margin-top: 20px;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.05);
        color: white;
    }
    .main-title {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.5rem;
        margin-bottom: -10px;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
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


def outcome_bar(h_win: float, draw: float, a_win: float, home: str, away: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=["Probability"],
            x=[h_win],
            orientation="h",
            name=f"{home} win",
            marker_color="#22d3ee",
            hovertemplate="<b>%{fullData.name}</b><br>%{x:.1%}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=["Probability"],
            x=[draw],
            orientation="h",
            name="Draw",
            marker_color="#64748b",
            base=[h_win],
            hovertemplate="<b>%{fullData.name}</b><br>%{x:.1%}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=["Probability"],
            x=[a_win],
            orientation="h",
            name=f"{away} win",
            marker_color="#0ea5e9",
            base=[h_win + draw],
            hovertemplate="<b>%{fullData.name}</b><br>%{x:.1%}<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="stack",
        height=140,
        margin=dict(l=24, r=24, t=8, b=24),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        xaxis=dict(tickformat=".0%", range=[0, 1], title=""),
        yaxis=dict(showticklabels=False, title=""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def league_quadrant_figure(power_df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        power_df,
        x="Scoring Power",
        y="Defensive Stability",
        text="Team",
        color="Scoring Power",
        color_continuous_scale="Viridis",
        labels={
            "Scoring Power": "Offensive rating (league avg = 100)",
            "Defensive Stability": "Defensive rating (league avg = 100)",
        },
        title="League efficiency quadrants",
        template="plotly_dark",
    )
    fig.add_hline(y=100, line_dash="dot", line_color="#444")
    fig.add_vline(x=100, line_dash="dot", line_color="#444")

    x0, x1 = power_df["Scoring Power"].min(), power_df["Scoring Power"].max()
    y0, y1 = power_df["Defensive Stability"].min(), power_df["Defensive Stability"].max()
    pad_x = (x1 - x0) * 0.06 + 1e-6
    pad_y = (y1 - y0) * 0.06 + 1e-6

    annotations = [
        ((x0 + 100) / 2, (y0 + 100) / 2, "Lower output"),
        ((100 + x1) / 2, (y0 + 100) / 2, "Attack-heavy"),
        ((x0 + 100) / 2, (100 + y1) / 2, "Defense-first"),
        ((100 + x1) / 2, (100 + y1) / 2, "Balanced / strong"),
    ]
    for xa, ya, label in annotations:
        fig.add_annotation(
            x=xa,
            y=ya,
            text=label,
            showarrow=False,
            font=dict(size=11, color="#6b7280"),
            xref="x",
            yref="y",
        )

    fig.update_traces(
        textposition="top center",
        marker=dict(size=12, line=dict(width=1, color="rgba(255,255,255,0.85)")),
    )
    fig.update_layout(
        font=dict(family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"),
        hoverlabel=dict(bgcolor="#111827", font_size=13),
        coloraxis_showscale=False,
        xaxis=dict(range=[x0 - pad_x, x1 + pad_x]),
        yaxis=dict(range=[y0 - pad_y, y1 + pad_y]),
    )
    return fig


avg_h, avg_a, h_att, h_def, a_att, a_def = load_league()
teams = sorted(h_att.index.tolist())

if "match_pred" not in st.session_state:
    with st.spinner("Computing default fixture (Arsenal vs Chelsea)…"):
        hw, d, aw = predict_match("Arsenal", "Chelsea", avg_h, avg_a, h_att, h_def, a_att, a_def)
    st.session_state["match_pred"] = {
        "home": "Arsenal",
        "away": "Chelsea",
        "h_win": hw,
        "draw": d,
        "a_win": aw,
    }

st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/Premier_League_Logo.svg/1024px-Premier_League_Logo.svg.png" width="120" style="filter: brightness(0.9) drop-shadow(0 4px 6px rgba(0,0,0,0.3));">
    </div>
    """, unsafe_allow_html=True
)
st.sidebar.header("Match setup")
home_team = st.sidebar.selectbox(
    "Home team",
    teams,
    index=team_index(teams, st.session_state["match_pred"]["home"]),
    key="sb_home",
)
away_team = st.sidebar.selectbox(
    "Away team",
    teams,
    index=team_index(teams, st.session_state["match_pred"]["away"]),
    key="sb_away",
)

if st.sidebar.button("Run simulation", type="primary", use_container_width=True):
    with st.spinner("Computing match probabilities…"):
        hw, d, aw = predict_match(home_team, away_team, avg_h, avg_a, h_att, h_def, a_att, a_def)
    st.session_state["match_pred"] = {
        "home": home_team,
        "away": away_team,
        "h_win": hw,
        "draw": d,
        "a_win": aw,
    }

pred = st.session_state["match_pred"]

st.markdown('<h1 class="main-title">Bet Intel</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Educational demo: Poisson-based 1X2 probabilities from completed-match data <br>(Premier League–style season in PostgreSQL).</p>', unsafe_allow_html=True)

tab_overview, tab_sim, tab_chart, tab_method = st.tabs(
    ["Overview", "Simulation", "League chart", "Methodology"]
)

with tab_overview:
    st.markdown(
        """
        **What this is:** A small analytics UI that estimates win / draw / loss probabilities
        using expected goals from team attack and defense indices, then a Poisson scoregrid (0–5 goals each side).

        **What it is not:** Betting advice, a live odds product, or a calibrated trading model.
        """
    )
    st.info(
        "**Disclaimer:** For portfolio and learning purposes only. Past results do not predict future "
        "matches; model simplifications (e.g. capped scorelines) mean probabilities are illustrative."
    )

with tab_sim:
    st.subheader("Match outcome")
    if home_team != pred["home"] or away_team != pred["away"]:
        st.warning("Sidebar teams differ from the last run. Click **Run simulation** in the sidebar to refresh.")
    
    st.markdown('<div class="match-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c1:
        img_url = TEAM_LOGOS.get(pred["home"], "https://upload.wikimedia.org/wikipedia/commons/e/e6/Football_logo.png")
        st.markdown(f'<img src="{img_url}" class="team-logo">', unsafe_allow_html=True)
        st.markdown(f'<div class="team-name">{pred["home"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="prob-val prob-home">{pred["h_win"]:.1%}</div>', unsafe_allow_html=True)
        st.markdown('<div class="prob-label">Win Probability</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="team-name" style="color: #64748b;">DRAW</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="prob-val prob-draw">{pred["draw"]:.1%}</div>', unsafe_allow_html=True)
        st.markdown('<div class="prob-label">Probability</div>', unsafe_allow_html=True)
        
    with c3:
        img_url = TEAM_LOGOS.get(pred["away"], "https://upload.wikimedia.org/wikipedia/commons/e/e6/Football_logo.png")
        st.markdown(f'<img src="{img_url}" class="team-logo">', unsafe_allow_html=True)
        st.markdown(f'<div class="team-name">{pred["away"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="prob-val prob-away">{pred["a_win"]:.1%}</div>', unsafe_allow_html=True)
        st.markdown('<div class="prob-label">Win Probability</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    total_p = pred["h_win"] + pred["draw"] + pred["a_win"]
    st.caption(
        f"Mass on 0–5 × 0–5 score grid: **{total_p:.1%}** of total probability "
        "(remainder is tails beyond five goals per side)."
    )
    st.plotly_chart(
        outcome_bar(pred["h_win"], pred["draw"], pred["a_win"], pred["home"], pred["away"]),
        use_container_width=True,
    )

power_df = pd.DataFrame(
    {
        "Team": h_att.index,
        "Scoring Power": (h_att.values * 100).round(1),
        "Defensive Stability": (1 / h_def.values * 100).round(1),
    }
)

with tab_chart:
    st.subheader("League efficiency map")
    st.markdown(
        "Teams indexed to **100 = league average**. "
        "**Top-right** is stronger attack and defense (by this crude measure); **bottom-left** is the opposite."
    )
    st.plotly_chart(league_quadrant_figure(power_df), use_container_width=True)

with tab_method:
    st.markdown(
        """
        **Data:** Finished matches (`status = 'FT'`) loaded via SQLAlchemy from PostgreSQL.

        **Indices:** Home attack / defense and away attack / defense are goal rates relative to league averages.

        **Expected goals:** For a chosen fixture, expected home and away goals are products of the relevant
        attack/defense factors and league average goals (home/away).

        **1X2 probabilities:** Independent Poisson distributions truncate at five goals per side; all
        scoreline probabilities in that grid are summed into home win, draw, and away win.
        """
    )

st.divider()
st.caption("Stack: Streamlit · Plotly · pandas · SciPy (Poisson) · PostgreSQL · SQLAlchemy")
