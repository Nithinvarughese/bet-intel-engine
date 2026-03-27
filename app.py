import base64
import html
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import get_league_averages_full, predict_match, get_team_form, get_h2h_matches
from manual_team_logos import manual_league_badge_url, resolve_manual_team_logo_url
from logos import (
    build_team_logo_map,
    fallback_avatar_url,
    fetch_image_bytes,
    fetch_league_logo_png,
    fetch_team_logo_png,
    resolve_team_id,
)

# Sidebar labels -> API-Football league ids (must match ingest.py LEAGUES_TO_FETCH)
LEAGUE_BY_LABEL = {
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61,
}

st.set_page_config(
    page_title="Bet Intel | Football analytics demo",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    
    .team-logo-wrap {
        text-align: center;
        width: 100%;
        margin: 0 0 6px 0;
    }
    .team-logo {
        display: inline-block;
        vertical-align: middle;
        height: 120px;
        width: auto;
        max-width: 120px;
        object-fit: contain;
        filter: drop-shadow(0px 10px 15px rgba(0, 0, 0, 0.5));
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), filter 0.4s ease;
    }
    .team-logo:hover {
        transform: scale(1.15) translateY(-5px);
        filter: drop-shadow(0px 15px 25px rgba(56, 189, 248, 0.4));
    }
    .sidebar-league-wrap {
        text-align: center;
        width: 100%;
        margin: 0 0 4px 0;
    }
    .sidebar-league-img {
        display: inline-block;
        vertical-align: middle;
        width: 104px;
        height: auto;
        max-height: 104px;
        object-fit: contain;
        filter: drop-shadow(0px 6px 12px rgba(0, 0, 0, 0.45));
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

    /* NEW: EV Glow Animation */
    @keyframes glowPulse {
        0% { box-shadow: 0 0 5px rgba(16, 185, 129, 0.2); border-color: rgba(16, 185, 129, 0.4); }
        50% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.8); border-color: rgba(16, 185, 129, 1); }
        100% { box-shadow: 0 0 5px rgba(16, 185, 129, 0.2); border-color: rgba(16, 185, 129, 0.4); }
    }
    .ev-positive {
        animation: glowPulse 2s infinite;
        border-radius: 12px;
        padding: 12px;
        margin-top: 10px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.5);
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data(ttl=3600, show_spinner="Loading league statistics…")
def load_league(league_id: int):
    return get_league_averages_full(league_id)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_team_logo_map(league_id: int):
    return build_team_logo_map(league_id)


@st.cache_data(ttl=86400, show_spinner=False)
def cached_team_logo_png(team_id: int):
    return fetch_team_logo_png(team_id)


@st.cache_data(ttl=86400, show_spinner=False)
def cached_image_bytes_from_url(url: str):
    return fetch_image_bytes(url)


@st.cache_data(ttl=86400, show_spinner=False)
def cached_league_logo_png(league_id: int):
    manual = manual_league_badge_url(league_id)
    if manual:
        blob = fetch_image_bytes(manual)
        if blob:
            return blob
    return fetch_league_logo_png(league_id)


def _image_blob_mime(blob: bytes) -> str:
    if blob.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if blob.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if blob.startswith(b"GIF87a") or blob.startswith(b"GIF89a"):
        return "image/gif"
    if len(blob) >= 12 and blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


def _render_centered_img(
    *,
    blob: bytes | None = None,
    url: str | None = None,
    width: int,
    img_class: str,
    wrap_class: str,
) -> None:
    if blob is not None:
        mime = _image_blob_mime(blob)
        b64 = base64.b64encode(blob).decode("ascii")
        src = f"data:{mime};base64,{b64}"
    elif url:
        src = url
    else:
        return
    safe_src = html.escape(src, quote=True)
    st.markdown(
        f'<div class="{html.escape(wrap_class)}">'
        f'<img class="{html.escape(img_class)}" src="{safe_src}" width="{width}" alt="" '
        f'style="max-width:{width}px;height:auto;" /></div>',
        unsafe_allow_html=True,
    )


def show_team_logo(team_name: str, logo_map: dict, league_id: int) -> None:
    w = 120
    manual = resolve_manual_team_logo_url(league_id, team_name)
    if manual:
        blob = cached_image_bytes_from_url(manual)
        if blob:
            _render_centered_img(
                blob=blob, width=w, img_class="team-logo", wrap_class="team-logo-wrap"
            )
            return
    tid = resolve_team_id(team_name, logo_map)
    if tid is not None:
        blob = cached_team_logo_png(int(tid))
        if blob:
            _render_centered_img(
                blob=blob, width=w, img_class="team-logo", wrap_class="team-logo-wrap"
            )
            return
    _render_centered_img(
        url=fallback_avatar_url(team_name),
        width=w,
        img_class="team-logo",
        wrap_class="team-logo-wrap",
    )


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

def simulate_season(teams, avg_h, avg_a, h_att, h_def, a_att, a_def):
    xPts = {t: 0.0 for t in teams}
    for home in teams:
        for away in teams:
            if home != away:
                preds = predict_match(home, away, avg_h, avg_a, h_att, h_def, a_att, a_def)
                xPts[home] += preds['h_win'] * 3 + preds['draw'] * 1
                xPts[away] += preds['a_win'] * 3 + preds['draw'] * 1
    
    df = pd.DataFrame(list(xPts.items()), columns=["Team", "Expected Points"])
    return df.sort_values("Expected Points", ascending=False).reset_index(drop=True)

if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = []
if 'bankroll' not in st.session_state:
    st.session_state['bankroll'] = 1000.0

def save_bet(match, selection, odds, prob, ev, recommended_wager_pct):
    st.session_state['portfolio'].append({
        "Match": match,
        "Selection": selection,
        "Odds": odds,
        "Model Prob": f"{prob:.1%}",
        "EV (%)": round(ev * 100, 1),
        "Suggested Stake": f"${st.session_state['bankroll'] * recommended_wager_pct:.2f} ({recommended_wager_pct:.1%})"
    })
    st.toast(f"Saved {selection} bet to Portfolio!")

# --- SIDEBAR: region first, then league badge (API-Sports CDN), then navigation ---
st.sidebar.markdown(
    '<h3 style="color: #cbd5e1; font-weight: 700; font-size:14px; margin-bottom:10px; letter-spacing:1px;">REGION</h3>',
    unsafe_allow_html=True,
)
league_label = st.sidebar.selectbox(
    "",
    list(LEAGUE_BY_LABEL.keys()),
    label_visibility="collapsed",
)
selected_league_id = LEAGUE_BY_LABEL[league_label]

_sb_l, _sb_c, _sb_r = st.sidebar.columns([1, 3, 1])
with _sb_c:
    _lg = cached_league_logo_png(selected_league_id)
    if _lg:
        _render_centered_img(
            blob=_lg,
            width=104,
            img_class="sidebar-league-img",
            wrap_class="sidebar-league-wrap",
        )
    else:
        _render_centered_img(
            url=fallback_avatar_url(league_label),
            width=104,
            img_class="sidebar-league-img",
            wrap_class="sidebar-league-wrap",
        )
st.sidebar.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

st.sidebar.markdown(
    '<h3 style="color: #cbd5e1; font-weight: 700; font-size:14px; margin-bottom:10px; letter-spacing:1px;">NAVIGATION</h3>',
    unsafe_allow_html=True,
)
app_mode = st.sidebar.radio(
    "",
    ["🏟️ Match Predictor", "📊 League Insights", "🔮 Season Simulator", "💰 Bet Portfolio"],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("Bet Intel Engine v2.0")

if "current_league_id" not in st.session_state:
    st.session_state["current_league_id"] = selected_league_id
elif st.session_state["current_league_id"] != selected_league_id:
    st.session_state["current_league_id"] = selected_league_id
    if "match_pred" in st.session_state:
        del st.session_state["match_pred"]

avg_h, avg_a, h_att, h_def, a_att, a_def = load_league(selected_league_id)

if h_att.empty:
    st.error(
        f"⚠️ **No finished matches for {league_label}** (league id `{selected_league_id}`). "
        "Add `FOOTBALL_API_KEY` to `.env`, then run **`python ingest.py`** once so rows get `league_id` populated."
    )
    st.stop()

teams = sorted(h_att.index.tolist())

if "match_pred" not in st.session_state:
    with st.spinner(f"Computing default fixture for {league_label}…"):
        default_home = teams[0] if len(teams) > 0 else "Home"
        default_away = teams[1] if len(teams) > 1 else "Away"
        preds = predict_match(default_home, default_away, avg_h, avg_a, h_att, h_def, a_att, a_def)
        preds["home_form"] = get_team_form(default_home, selected_league_id)
        preds["away_form"] = get_team_form(default_away, selected_league_id)
        preds["h2h"] = get_h2h_matches(default_home, default_away, selected_league_id)
    preds["home"] = default_home
    preds["away"] = default_away
    st.session_state["match_pred"] = preds

if app_mode == "📊 League Insights":
    st.markdown('<h1 class="main-title">LEAGUE INSIGHTS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">MACRO PERFORMANCE DATA</p>', unsafe_allow_html=True)
    
    power_df = pd.DataFrame(
        {
            "Team": h_att.index,
            "Scoring Power": (h_att.values * 100).round(1),
            "Defensive Stability": (1 / h_def.values * 100).round(1),
        }
    )
    st.plotly_chart(power_rankings_figure(power_df), use_container_width=True)
    st.info("Future features like Top Scorers and Form Tables will be integrated here.")
    st.stop()

elif app_mode == "🔮 Season Simulator":
    st.markdown('<h1 class="main-title">SEASON SIMULATOR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Expected Points Engine</p>', unsafe_allow_html=True)
    
    with st.spinner("Simulating the entire 38-game season (380 Matches)..."):
        sim_df = simulate_season(teams, avg_h, avg_a, h_att, h_def, a_att, a_def)
    
    st.markdown('<div class="match-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color:#f8fafc; font-weight:700; margin-bottom: 10px;">Projected Final League Table</h3>', unsafe_allow_html=True)
    st.caption("Based on cumulative Expected Points (xPts) for every single home and away permutation utilizing our Poisson mathematical distribution engine.")
    
    sim_df.index = sim_df.index + 1
    sim_df["Expected Points"] = sim_df["Expected Points"].round(1)
    
    st.dataframe(
        sim_df, 
        use_container_width=True, 
        height=600,
        column_config={
            "Team": st.column_config.TextColumn("Club"),
            "Expected Points": st.column_config.ProgressColumn(
                 "Projected xPTS", min_value=0, max_value=114, format="%.1f"
            )
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

elif app_mode == "💰 Bet Portfolio":
    st.markdown('<h1 class="main-title">BET PORTFOLIO</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">VALUE TRACKER</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="match-card">', unsafe_allow_html=True)
    if not st.session_state['portfolio']:
        st.info("No bets placed yet. Navigate to the **🏟️ Match Predictor** and track some +EV bets!")
    else:
        portfolio_df = pd.DataFrame(st.session_state['portfolio'])
        
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Mock Bankroll", f"${st.session_state['bankroll']:,.2f}")
        col_s2.metric("Total Bets Tracked", len(portfolio_df))
        col_s3.metric("Avg Expected ROI", f"{portfolio_df['EV (%)'].mean():.1f}%")
        
        st.markdown('<h3 style="color:#f8fafc; font-weight:700; margin-top: 30px; margin-bottom: 10px;">My Saved Bets Ledger</h3>', unsafe_allow_html=True)
        st.dataframe(portfolio_df, hide_index=True, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("🗑️ Clear Portfolio", type="secondary"):
                st.session_state['portfolio'] = []
                st.rerun()
        with col_btn2:
            st.caption("Bets are sized according to the Kelly Criterion to maximize long-term bankroll growth.")
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.markdown('<h1 class="main-title">BET INTEL</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">PREDICTIVE ANALYTICS ENGINE</p>', unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px 30px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 35px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);">
""", unsafe_allow_html=True)

c_home, c_vs, c_away, c_btn = st.columns([3, 1, 3, 2])
with c_home:
    home_team = st.selectbox("Home Team", teams, index=team_index(teams, st.session_state["match_pred"]["home"]), key="sb_home")
    h_adj = st.slider("Attack Condition (%)", -50, 50, 0, 5, help="Adjust if star attacker is missing / returning.")
with c_vs:
    st.markdown('<div style="text-align:center; font-size: 18px; font-weight:800; margin-top:32px; color:#64748b;">VS</div>', unsafe_allow_html=True)
with c_away:
    away_team = st.selectbox("Away Team", teams, index=team_index(teams, st.session_state["match_pred"]["away"]), key="sb_away")
    a_adj = st.slider("Defense Condition (%)", -50, 50, 0, 5, help="Adjust if star defender is missing / returning.")
with c_btn:
    st.markdown('<div style="margin-top:28px;"></div>', unsafe_allow_html=True)
    if st.button("RUN SIMULATION", type="primary", use_container_width=True):
        with st.spinner("Computing match probabilities…"):
            h_att_adj = h_att.copy()
            a_def_adj = a_def.copy()
            h_att_adj[home_team] *= (1 + h_adj/100.0)
            a_def_adj[away_team] *= (1 + a_adj/100.0)
            
            preds = predict_match(home_team, away_team, avg_h, avg_a, h_att_adj, h_def, a_att, a_def_adj)
            preds["home_form"] = get_team_form(home_team, selected_league_id)
            preds["away_form"] = get_team_form(away_team, selected_league_id)
            preds["h2h"] = get_h2h_matches(home_team, away_team, selected_league_id)
        preds["home"] = home_team
        preds["away"] = away_team
        st.session_state["match_pred"] = preds

st.markdown("</div>", unsafe_allow_html=True)

pred = st.session_state["match_pred"]
team_logo_map = cached_team_logo_map(selected_league_id)

if home_team != pred["home"] or away_team != pred["away"]:
    st.warning("Selected teams differ from the displayed simulation. Click **RUN SIMULATION** to update.")

st.markdown('<div class="match-card">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    show_team_logo(pred["home"], team_logo_map, selected_league_id)
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
    show_team_logo(pred["away"], team_logo_map, selected_league_id)
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
    st.markdown('<h3 style="color:#f8fafc; font-weight:700; margin-bottom: 20px;">Match Probability</h3>', unsafe_allow_html=True)
    st.plotly_chart(
        outcome_donut(pred["h_win"], pred["draw"], pred["a_win"], pred["home"], pred["away"]),
        use_container_width=True,
    )
    
    total_p = pred["h_win"] + pred["draw"] + pred["a_win"]
    st.caption(
        f"**Mathematical Note:** Independent Poisson model grid (capped at 5 goals per side). "
        f"Distribution covers **{total_p:.1%}** of total probability space."
    )
    st.markdown('<h3 style="color:#f8fafc; font-weight:700; margin-top: 40px; margin-bottom: 20px;">Recent Head-to-Head</h3>', unsafe_allow_html=True)
    h2h_df = pred.get("h2h")
    if h2h_df is not None and not h2h_df.empty:
        h2h_display = h2h_df.copy()
        h2h_display['Date'] = pd.to_datetime(h2h_display['match_date'], errors='coerce').dt.strftime('%b %d, %Y')
        h2h_display['Score'] = h2h_display['home_team'] + " " + h2h_display['home_goals'].astype(str) + " - " + h2h_display['away_goals'].astype(str) + " " + h2h_display['away_team']
        st.dataframe(h2h_display[['Date', 'Score']], hide_index=True, use_container_width=True)
    else:
        st.info("No recent head-to-head matches found in database.")

with col_right:
    st.markdown('<h3 style="color:#f8fafc; font-weight:700; margin-bottom: 20px;">Score Heatmap</h3>', unsafe_allow_html=True)
    st.plotly_chart(score_heatmap(pred["score_matrix"], pred["home"], pred["away"]), use_container_width=True)

st.markdown("---")

with st.expander("💰 Expected Value (EV) Analyzer", expanded=True):
    st.markdown('<h4 style="color:#f8fafc; font-weight:700; margin-bottom: 10px;">Find Value Bets</h4>', unsafe_allow_html=True)
    st.caption("Enter live bookmaker Decimal Odds below to calculate the Expected Value (EV) over the long run, comparing our model's probability against the bookie's implied probability.")
    
    def render_ev_col(selection_name, prob, odds_val, odds_key, btn_key):
        odds = st.number_input(f"{selection_name} Odds", min_value=1.01, value=odds_val, step=0.1, key=odds_key)
        ev = (prob * odds) - 1
        kelly = 0
        if ev > 0:
            b = odds - 1
            kelly = max(0, (prob * b - (1 - prob)) / b)
            st.markdown(f'''
            <div class="ev-positive">
                <div style="color: #10b981; font-weight: 800; font-size: 16px;">🔥 +EV Found! ({ev:+.1%} ROI)</div>
                <div style="color: #cbd5e1; font-size: 13px; margin-top: 4px;">Kelly Stake: <b>{kelly:.1%}</b> (${st.session_state["bankroll"] * kelly:.2f})</div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.error(f"Negative EV ({ev:+.1%} ROI)")
            
        if st.button(f"Track {selection_name}", key=btn_key): 
            save_bet(f"{pred['home']} vs {pred['away']}", selection_name, odds, prob, ev, kelly)

    col_ev1, col_ev2, col_ev3 = st.columns(3)
    with col_ev1:
        render_ev_col(pred['home'], pred['h_win'], 2.50, "odd_h", "btn_h")
    with col_ev2:
        render_ev_col("Draw", pred['draw'], 3.20, "odd_d", "btn_d")
    with col_ev3:
        render_ev_col(pred['away'], pred['a_win'], 2.80, "odd_a", "btn_a")

st.divider()
st.caption("Stack: Streamlit · Plotly · pandas · SciPy (Poisson) · PostgreSQL · SQLAlchemy")
