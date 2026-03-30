import base64
import html
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import get_league_averages_full, predict_match, get_team_form, get_h2h_matches, get_last_refresh_timestamp
from plotly_theme import apply_theme
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

# Main-area navigation (order must match existing `app_mode` branches below)
NAV_MODES = (
    "🏟️ Match Predictor",
    "📊 League Insights",
    "🔮 Season Simulator",
    "💰 Bet Portfolio",
)


def _nav_segment_label(option: str) -> str:
    """Shorter dock labels; return value from widget stays the full NAV_MODES string."""
    return {
        "🏟️ Match Predictor": "Match lab",
        "📊 League Insights": "League",
        "🔮 Season Simulator": "Season",
        "💰 Bet Portfolio": "Portfolio",
    }.get(option, option)

st.set_page_config(
    page_title="Pitch Metrics | Football analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;700;900&display=swap');

    :root {
        --surface-0: #080612;
        --surface-1: rgba(18, 12, 38, 0.85);
        --surface-2: rgba(32, 20, 60, 0.75);
        --border-subtle: rgba(255, 255, 255, 0.07);
        --text-primary: #faf5ff;
        --text-muted: #c4b5fd;
        --text-dim: #7c6fa0;
        --accent: #f59e0b;
        --accent-glow: rgba(245, 158, 11, 0.35);
        --accent2: #a78bfa;
        --radius: 12px;
        --shadow-1: 0 10px 20px -4px rgba(0, 0, 0, 0.5);
        --shadow-2: 0 30px 60px -15px rgba(0, 0, 0, 0.7);
        --max-width: 1320px;
    }

    /* Max Width Constraint */
    .main-app-container {
        max-width: var(--max-width);
        margin: 0 auto;
        padding: 0 24px;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-muted);
    }
    h1, h2, h3, h4, h5, h6, .team-name, .prob-val, .hero-title {
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }

    /* Tabular Numerics */
    .tabular-nums { font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; }

    [data-testid="stAppViewContainer"] {
        background-color: var(--surface-0);
        background-image:
            radial-gradient(ellipse at 20% 0%, rgba(109, 40, 217, 0.25) 0, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(245, 158, 11, 0.12) 0, transparent 50%);
        background-attachment: fixed;
    }

    /* Hero Lockup */
    .hero-container {
        padding: 64px 0 32px 0;
        text-align: center;
    }
    .hero-title {
        font-size: 5rem;
        font-weight: 900;
        margin-bottom: 4px;
        letter-spacing: -4px;
        background: linear-gradient(135deg, #fff 30%, #a78bfa 70%, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .hero-subtitle {
        color: var(--accent);
        letter-spacing: 0.5em;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: -8px;
    }
    .hero-rule {
        width: 40px; height: 2px;
        background: var(--accent);
        margin: 16px auto 0 auto;
        border-radius: 2px;
    }

    /* Top nav — glass pill dock (segmented control) */
    div[data-testid="stSegmentedControl"] {
        width: 100%;
        max-width: 820px;
        margin: 16px auto 32px auto;
        padding: 0;
    }
    div[data-testid="stSegmentedControl"] [data-baseweb="segmented-control"] {
        width: 100% !important;
        background: linear-gradient(
            155deg,
            rgba(32, 22, 58, 0.55) 0%,
            rgba(12, 8, 28, 0.72) 100%
        ) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(167, 139, 250, 0.22) !important;
        border-radius: 999px !important;
        padding: 5px !important;
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(0, 0, 0, 0.35) inset,
            0 1px 0 rgba(255, 255, 255, 0.07) inset !important;
    }
    div[data-testid="stSegmentedControl"] [role="tablist"],
    div[data-testid="stSegmentedControl"] [data-baseweb="segmented-control"] > div:first-child {
        width: 100% !important;
        display: flex !important;
        align-items: stretch !important;
        gap: 4px !important;
    }
    div[data-testid="stSegmentedControl"] button {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.8125rem !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        color: var(--text-dim) !important;
        background: transparent !important;
        border: none !important;
        border-radius: 999px !important;
        margin: 0 !important;
        min-height: 44px !important;
        padding: 0 0.85rem !important;
        flex: 1 1 0 !important;
        transition: color 0.2s ease, background 0.2s ease, box-shadow 0.25s ease, transform 0.15s ease !important;
    }
    div[data-testid="stSegmentedControl"] button:hover {
        color: var(--text-primary) !important;
        background: rgba(255, 255, 255, 0.07) !important;
    }
    div[data-testid="stSegmentedControl"] button:focus-visible {
        outline: 2px solid var(--accent2) !important;
        outline-offset: 2px !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-selected="true"],
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        color: #0c0818 !important;
        background: linear-gradient(135deg, #f0e7ff 0%, #fde68a 48%, #f59e0b 100%) !important;
        box-shadow:
            0 4px 20px rgba(245, 158, 11, 0.28),
            0 0 28px rgba(167, 139, 250, 0.18) !important;
        font-weight: 800 !important;
    }
    @media (prefers-reduced-motion: reduce) {
        div[data-testid="stSegmentedControl"] button {
            transition: none !important;
        }
    }

    /* Elevation System */
    .panel-default {
        background: var(--surface-1);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius);
        padding: 24px;
        box-shadow: var(--shadow-1);
        margin-bottom: 24px;
    }
    .card-elevated {
        background: linear-gradient(145deg, rgba(32, 20, 60, 0.85) 0%, rgba(15, 10, 35, 0.95) 100%);
        border: 1px solid rgba(167, 139, 250, 0.15);
        border-radius: 24px;
        padding: 40px 32px;
        box-shadow: var(--shadow-2);
        backdrop-filter: blur(32px);
        position: relative;
        overflow: hidden;
    }
    .card-elevated::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 1.5px;
        background: linear-gradient(90deg, transparent, var(--accent), var(--accent2), transparent);
        opacity: 0.8;
    }
    .card-elevated::after {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at 50% -10%, rgba(109, 40, 217, 0.12), transparent 65%);
        pointer-events: none;
    }

    /* Section Labels */
    .section-label {
        font-size: 0.7rem;
        font-weight: 800;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin-top: 48px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .section-label::after { content: ""; flex: 1; height: 1px; background: var(--border-subtle); }

    /* Performance Feedback */
    .updated-badge {
        font-size: 0.65rem;
        color: #10b981;
        background: rgba(16, 185, 129, 0.08);
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid rgba(16, 185, 129, 0.15);
        display: inline-block;
        margin-top: 16px;
    }

    /* Tab Padding Injection */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 2rem !important;
    }

    /* Empty State styles */
    .empty-illustration {
        width: 100px; height: 100px;
        margin: 0 auto 16px auto;
        position: relative;
        display: flex; align-items: center; justify-content: center;
    }
    .empty-shape {
        position: absolute;
        width: 100%; height: 100%;
        border: 2px dashed var(--text-dim);
        border-radius: 50%;
        animation: rotate 20s linear infinite;
        opacity: 0.2;
    }
    /* Team Logo — centered inline in HTML block */
    .team-logo-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 110px;
        margin-bottom: 8px;
    }
    .team-logo {
        max-height: 90px;
        max-width: 90px;
        width: auto;
        height: auto;
        object-fit: contain;
        filter: drop-shadow(0 6px 16px rgba(0,0,0,0.5));
        transition: transform 0.3s ease, filter 0.3s ease;
    }
    .team-logo:hover { transform: translateY(-4px) scale(1.08); filter: drop-shadow(0 10px 24px rgba(56,189,248,0.35)); }

    /* Team Name */
    .team-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        text-align: center;
        margin: 4px 0 10px 0;
        letter-spacing: -0.01em;
    }

    /* Form Badges */
    .form-row { display: flex; justify-content: center; gap: 5px; margin-bottom: 20px; }
    .form-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px; height: 22px;
        border-radius: 6px;
        font-size: 10px; font-weight: 800;
        letter-spacing: 0;
        line-height: 1;
    }
    .form-W { background: #059669; color: #ecfdf5; box-shadow: 0 2px 6px rgba(5,150,105,0.4); }
    .form-D { background: #475569; color: #e2e8f0; box-shadow: 0 2px 6px rgba(71,85,105,0.4); }
    .form-L { background: #dc2626; color: #fef2f2; box-shadow: 0 2px 6px rgba(220,38,38,0.4); }

    /* Premium Probability Display */
    .prob-block { text-align: center; margin-top: 4px; }
    .prob-val {
        font-size: 3rem;
        font-weight: 900;
        line-height: 1;
        letter-spacing: -2px;
        font-variant-numeric: tabular-nums;
        font-feature-settings: "tnum";
    }
    .prob-h { color: #f59e0b; text-shadow: 0 0 32px rgba(245,158,11,0.55); }
    .prob-d { color: #a78bfa; font-size: 2.2rem; }
    .prob-a { color: #c084fc; text-shadow: 0 0 32px rgba(192,132,252,0.55); }
    .prob-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--text-dim);
        font-weight: 700;
        margin-top: 6px;
    }

    /* Draw separator */
    .draw-col {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        height: 100%;
        padding-bottom: 4px;
    }
    .vs-line {
        width: 1px; height: 40px;
        background: linear-gradient(to bottom, transparent, var(--border-subtle), transparent);
        margin-bottom: 16px;
    }

    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .empty-icon { font-size: 2rem; opacity: 0.5; }

    @media (prefers-reduced-motion: reduce) {
        * { animation: none !important; transition: none !important; transform: none !important; }
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
                    color_continuous_scale="Purp", text_auto=".1%")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c4b5fd"),
        height=380, margin=dict(t=20, b=20, l=20, r=20)
    )
    fig.update_xaxes(side="top")
    return apply_theme(fig)


def outcome_donut(h_win: float, draw: float, a_win: float, home: str, away: str) -> go.Figure:
    fig = go.Figure(data=[go.Pie(
        labels=[f"{home}", "Draw", f"{away}"],
        values=[h_win, draw, a_win],
        hole=.65,
        marker=dict(colors=["#f59e0b", "#6d28d9", "#c084fc"], line=dict(color='#080612', width=3)),
        textinfo='percent',
        hoverinfo='label+percent',
        textfont=dict(size=18, color="white")
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5, font=dict(color="#c4b5fd", size=14)),
        margin=dict(t=30, b=30, l=20, r=20),
    )
    return apply_theme(fig)


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
        xaxis=dict(title="Overall Rating (100 = Average)"),
        yaxis=dict(title="", tickfont=dict(size=14)),
        height=450,
        margin=dict(t=50, b=30, l=20, r=20),
    )
    return apply_theme(fig)

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

st.sidebar.divider()
st.sidebar.caption("Pitch Metrics v2.1")

# --- NEW: Max Width Wrapper ---
st.markdown('<div class="main-app-container">', unsafe_allow_html=True)

if "current_league_id" not in st.session_state:
    st.session_state["current_league_id"] = selected_league_id
elif st.session_state["current_league_id"] != selected_league_id:
    # League changed: Prompt for re-run
    st.session_state["current_league_id"] = selected_league_id
    st.session_state["league_changed"] = True
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

# --- NEW: Hero Header ---
st.markdown(f'''
    <div class="hero-container">
        <div class="hero-title">Pitch Metrics</div>
        <div class="hero-subtitle">Match &amp; league analytics</div>
        <div class="hero-rule"></div>
    </div>
''', unsafe_allow_html=True)

# --- NEW: Sticky Subheader ---
last_update = get_last_refresh_timestamp(selected_league_id)
update_str = last_update.strftime("%b %d, %Y") if last_update else "No data"
st.markdown(f'''
    <div class="subheader-bar">
        <div>
            <span class="subheader-label">LEAGUE:</span>
            <span class="subheader-val">{league_label}</span>
        </div>
        <div>
            <span class="subheader-label">LAST REFRESH:</span>
            <span class="subheader-val">{update_str}</span>
        </div>
    </div>
''', unsafe_allow_html=True)

app_mode = st.segmented_control(
    "Section",
    options=list(NAV_MODES),
    default=NAV_MODES[0],
    format_func=_nav_segment_label,
    key="pitch_top_nav",
    label_visibility="collapsed",
    width="stretch",
)

if "match_pred" not in st.session_state:
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
    st.markdown('''
        <div class="hero-container" style="padding: 40px 0 20px 0;">
            <div class="hero-title" style="font-size:3.5rem;">SEASON SIMULATOR</div>
            <div class="hero-subtitle">POISSON EXPECTED POINTS ENGINE</div>
            <div class="hero-rule"></div>
        </div>
    ''', unsafe_allow_html=True)

    with st.spinner("Simulating full 38-game season…"):
        sim_df = simulate_season(teams, avg_h, avg_a, h_att, h_def, a_att, a_def)

    team_logo_map_sim = cached_team_logo_map(selected_league_id)
    sim_df.index = sim_df.index + 1
    sim_df["Expected Points"] = sim_df["Expected Points"].round(1)
    max_pts = sim_df["Expected Points"].max()

    # Medal styles for top-3
    RANK_STYLES = {
        1: ("🥇", "#f59e0b", "rgba(245,158,11,0.12)", "rgba(245,158,11,0.3)"),
        2: ("🥈", "#94a3b8", "rgba(148,163,184,0.08)", "rgba(148,163,184,0.2)"),
        3: ("🥉", "#a16207", "rgba(161,98,7,0.08)", "rgba(161,98,7,0.2)"),
    }

    # Build rows HTML
    rows_html = ""
    for rank, row in sim_df.iterrows():
        team_name = row["Team"]
        xpts = row["Expected Points"]
        pct = xpts / max_pts * 100

        # Get logo as base64
        logo_html = ""
        manual = resolve_manual_team_logo_url(selected_league_id, team_name)
        blob = None
        if manual:
            blob = cached_image_bytes_from_url(manual)
        if not blob:
            tid = resolve_team_id(team_name, team_logo_map_sim)
            if tid is not None:
                blob = cached_team_logo_png(int(tid))
        if blob:
            mime = _image_blob_mime(blob)
            b64 = base64.b64encode(blob).decode("ascii")
            logo_html = f'<img src="data:{mime};base64,{b64}" style="width:32px;height:32px;object-fit:contain;vertical-align:middle;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.5));" />'

        medal, accent, row_bg, bar_color = RANK_STYLES.get(rank, ("", "var(--text-dim)", "transparent", "rgba(167,139,250,0.25)"))
        rank_cell = f'<span style="font-size:1.1rem;">{medal}</span>' if medal else f'<span style="font-size:0.9rem;font-weight:800;color:var(--text-dim);">{rank}</span>'

        # CL / relegation zone hint
        zone_dot = ""
        if rank <= 4:
            zone_dot = '<span style="display:inline-block;width:6px;height:6px;background:#f59e0b;border-radius:50%;margin-left:6px;vertical-align:middle;"></span>'
        elif rank >= len(sim_df) - 2:
            zone_dot = '<span style="display:inline-block;width:6px;height:6px;background:#ef4444;border-radius:50%;margin-left:6px;vertical-align:middle;"></span>'

        rows_html += f'''
        <tr style="background:{row_bg}; transition: background 0.2s;">
            <td style="width:50px;text-align:center;padding:12px 8px;">{rank_cell}</td>
            <td style="padding:12px 12px 12px 4px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    {logo_html}
                    <span style="font-weight:700;color:var(--text-primary);font-family:'Outfit',sans-serif;font-size:1rem;">{html.escape(team_name)}</span>
                    {zone_dot}
                </div>
            </td>
            <td style="width:260px;padding:12px 16px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="flex:1;height:6px;border-radius:3px;background:rgba(255,255,255,0.06);">
                        <div style="width:{pct:.1f}%;height:100%;border-radius:3px;background:linear-gradient(90deg,{accent},{bar_color});transition:width 0.6s ease;"></div>
                    </div>
                    <span style="font-size:1.1rem;font-weight:900;color:{accent};font-family:'Outfit',sans-serif;font-variant-numeric:tabular-nums;min-width:38px;text-align:right;">{xpts}</span>
                </div>
            </td>
        </tr>'''

    # Legend
    legend = '''
    <div style="display:flex;gap:20px;margin-top:20px;font-size:0.7rem;color:var(--text-dim);">
        <span><span style="display:inline-block;width:8px;height:8px;background:#f59e0b;border-radius:50%;margin-right:4px;vertical-align:middle;"></span>Champions League Zone</span>
        <span><span style="display:inline-block;width:8px;height:8px;background:#ef4444;border-radius:50%;margin-right:4px;vertical-align:middle;"></span>Relegation Zone</span>
        <span style="margin-left:auto;">xPTS = Expected Points (Poisson model, 380 fixtures)</span>
    </div>'''

    table_html = f'''
    <div style="background:linear-gradient(145deg,rgba(32,20,60,0.85),rgba(15,10,35,0.95));border:1px solid rgba(167,139,250,0.15);border-radius:20px;padding:28px;box-shadow:0 30px 60px -15px rgba(0,0,0,0.7);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <div style="font-family:Outfit,sans-serif;font-size:1.15rem;font-weight:800;color:var(--text-primary);">Projected Final Standings</div>
            <div style="font-size:0.75rem;color:var(--text-dim);letter-spacing:1px;">38 GAME SEASON · xPTS</div>
        </div>
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.07);">
                    <th style="padding:6px 8px;font-size:0.65rem;color:var(--text-dim);text-align:center;font-weight:700;letter-spacing:1.5px;">#</th>
                    <th style="padding:6px 12px;font-size:0.65rem;color:var(--text-dim);text-align:left;font-weight:700;letter-spacing:1.5px;">CLUB</th>
                    <th style="padding:6px 16px;font-size:0.65rem;color:var(--text-dim);text-align:left;font-weight:700;letter-spacing:1.5px;">xPTS</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        {legend}
    </div>'''

    st.html(table_html)
    st.stop()

elif app_mode == "💰 Bet Portfolio":
    st.markdown('<h1 class="main-title">BET PORTFOLIO</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">VALUE TRACKER</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="match-card">', unsafe_allow_html=True)
    if not st.session_state['portfolio']:
        st.info("No bets saved yet. Open **🏟️ Match Predictor** (top) and add +EV picks to your ledger.")
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

# --- 2-COLUMN MATCH PREDICTOR ---
col_ctrl, col_main = st.columns([1, 2.5], gap="large")

with col_ctrl:
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.subheader("Match Selection")
    h_team = st.selectbox("Home", teams, index=team_index(teams, st.session_state["match_pred"]["home"]), key="ctrl_home")
    a_team = st.selectbox("Away", teams, index=team_index(teams, st.session_state["match_pred"]["away"]), key="ctrl_away")
    
    st.divider()
    st.subheader("Conditions")
    h_adj = st.slider("Home Attack (%)", -50, 50, 0, 5, help="Adjust for injuries/morale")
    a_adj = st.slider("Away Defense (%)", -50, 50, 0, 5)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("RUN SIMULATION", type="primary", use_container_width=True)
    if run_btn:
        with st.spinner("Calculating..."):
            h_att_adj = h_att.copy()
            a_def_adj = a_def.copy()
            h_att_adj[h_team] *= (1 + h_adj/100.0)
            a_def_adj[a_team] *= (1 + a_adj/100.0)
            
            res = predict_match(h_team, a_team, avg_h, avg_a, h_att_adj, h_def, a_att, a_def_adj)
            res["home_form"] = get_team_form(h_team, selected_league_id)
            res["away_form"] = get_team_form(a_team, selected_league_id)
            res["h2h"] = get_h2h_matches(h_team, a_team, selected_league_id)
            res["home"] = h_team
            res["away"] = a_team
            res["updated"] = True
            st.session_state["match_pred"] = res
            st.session_state["league_changed"] = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_main:
    if st.session_state.get("league_changed"):
        st.markdown('<div class="panel-default" style="margin-bottom:24px; border-left: 4px solid var(--accent);">🔄 <b>League Change Detected.</b> Click RUN SIMULATION to refresh the predictive model.</div>', unsafe_allow_html=True)

    pred = st.session_state["match_pred"]
    team_logo_map = cached_team_logo_map(selected_league_id)
    
    # Hero Result Card — rendered entirely as one HTML block for alignment
    st.markdown('<div class="section-label">MATCH OUTCOME</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-elevated animate-in">', unsafe_allow_html=True)
        r1, r2, r3 = st.columns([5, 3, 5])
        
        with r1:
            # Logo + name + form + prob all as a single block
            home_form_html = "".join([f'<span class="form-badge form-{r}">{r}</span>' for r in pred["home_form"]])
            # Render logo
            show_team_logo(pred["home"], team_logo_map, selected_league_id)
            st.markdown(f'''
                <div class="team-name">{pred["home"]}</div>
                <div class="form-row">{home_form_html}</div>
                <div class="prob-block">
                    <div class="prob-val prob-h">{pred["h_win"]:.1%}</div>
                    <div class="prob-label">Home Win</div>
                </div>
            ''', unsafe_allow_html=True)
            
        with r2:
            st.markdown(f'''
                <div class="draw-col">
                    <div class="vs-line"></div>
                    <div class="team-name" style="color:var(--text-dim); font-size:0.85rem; letter-spacing:3px;">DRAW</div>
                    <div class="prob-val prob-d" style="font-size:2rem; margin-top:8px;">{pred["draw"]:.1%}</div>
                    <div class="prob-label">Probability</div>
                </div>
            ''', unsafe_allow_html=True)
            
        with r3:
            away_form_html = "".join([f'<span class="form-badge form-{r}">{r}</span>' for r in pred["away_form"]])
            show_team_logo(pred["away"], team_logo_map, selected_league_id)
            st.markdown(f'''
                <div class="team-name">{pred["away"]}</div>
                <div class="form-row">{away_form_html}</div>
                <div class="prob-block">
                    <div class="prob-val prob-a">{pred["a_win"]:.1%}</div>
                    <div class="prob-label">Away Win</div>
                </div>
            ''', unsafe_allow_html=True)
        
        if pred.get("updated"):
            st.markdown('<div style="text-align:right; margin-top:16px;"><span class="updated-badge">✓ UPDATED</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Key Stat Row - REDESIGNED for spacing
    st.markdown('<div class="section-label">SECONDARY METRICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-default">', unsafe_allow_html=True)
    mk1, mk2 = st.columns([1, 1], gap="large")
    with mk1:
        st.metric("Both Teams to Score", f"{pred['btts']:.1%}", help="Probability of both sides scoring at least 1 goal")
    with mk2:
        st.metric("Over 2.5 Goals", f"{pred['over_25']:.1%}", f"{pred['under_25']:.1%} under", delta_color="off")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Tabs
    st.markdown('<div class="section-label">ANALYTICS & CONTEXT</div>', unsafe_allow_html=True)
    tab_ana, tab_h2h, tab_ev = st.tabs(["📊 Probability Analysis", "⚔️ Head to Head", "💰 Value Tracker"])
    
    with tab_ana:
        st.markdown('<div class="panel-default">', unsafe_allow_html=True)
        la, ra = st.columns([1, 1])
        with la:
            st.plotly_chart(outcome_donut(pred["h_win"], pred["draw"], pred["a_win"], pred["home"], pred["away"]), use_container_width=True)
        with ra:
            with st.expander("🔥 View Full Score Heatmap", expanded=False):
                st.plotly_chart(score_heatmap(pred["score_matrix"], pred["home"], pred["away"]), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
    with tab_h2h:
        st.markdown('<div class="panel-default">', unsafe_allow_html=True)
        h2h_df = pred.get("h2h")
        if h2h_df is not None and not h2h_df.empty:
            st.dataframe(h2h_df[['match_date', 'home_team', 'home_goals', 'away_goals', 'away_team']], hide_index=True, use_container_width=True)
        else:
            st.markdown('''
            <div style="text-align:center; padding: 40px;">
                <div class="empty-illustration">
                    <div class="empty-shape"></div>
                    <div class="empty-icon">⚔️</div>
                </div>
                <div style="color:var(--text-primary); font-weight:700;">No Recent Encounters</div>
                <div style="font-size:0.8rem; color:var(--text-dim);">Historical data for this specific fixture is not available in our current dataset.</div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
    with tab_ev:
        st.markdown('<div class="panel-default">', unsafe_allow_html=True)
        st.caption("Enter Decimal Odds to find +EV bets with Kelly sizing.")
        def render_ev_item(label, prob, val, key):
            odds = st.number_input(f"{label} Odds", 1.01, 50.0, val, 0.1, key=f"ev_{key}")
            ev = (prob * odds) - 1
            if ev > 0:
                b = odds - 1
                k = max(0, (prob*b - (1-prob))/b)
                st.markdown(f'''<div class="ev-positive"><b style="color:#10b981;">🔥 Edge Found: {ev:+.1%}</b><br><span style="font-size:0.8rem; color:var(--text-muted);">Kelly Stake: {k:.1%} (${st.session_state['bankroll']*k:.2f})</span></div>''', unsafe_allow_html=True)
                if st.button(f"Track {label}", key=f"btn_{key}"):
                    save_bet(f"{pred['home']} v {pred['away']}", label, odds, prob, ev, k)
            else:
                st.error(f"Loss: {ev:+.1%}")

        e1, e2, e3 = st.columns(3)
        with e1: render_ev_item(pred['home'], pred['h_win'], 2.5, "h")
        with e2: render_ev_item("Draw", pred['draw'], 3.2, "d")
        with e3: render_ev_item(pred['away'], pred['a_win'], 2.8, "a")
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption("Pitch Metrics 2.1 • Slate & Cyan design system")
st.markdown('</div>', unsafe_allow_html=True) # End main-app-container
