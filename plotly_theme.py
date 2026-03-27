# Plotly Theme Configuration for Bet Intel

# Tokens mapping to CSS variables in app.py
TOKENS = {
    "bg_deep": "#0b1120",
    "surface_1": "rgba(30, 41, 59, 0.7)",
    "text_main": "#f8fafc",
    "text_muted": "#94a3b8",
    "accent": "#38bdf8",
    "grid": "rgba(255, 255, 255, 0.05)"
}

def get_base_layout():
    """Returns standard layout dictionary for Plotly charts."""
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Outfit, Inter, sans-serif", color=TOKENS["text_muted"], size=12),
        margin=dict(t=40, b=40, l=40, r=40),
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=13,
            font_family="Inter, sans-serif"
        ),
        xaxis=dict(
            gridcolor=TOKENS["grid"],
            zerolinecolor=TOKENS["grid"],
            tickfont=dict(color=TOKENS["text_dim"] if "text_dim" in TOKENS else TOKENS["text_muted"])
        ),
        yaxis=dict(
            gridcolor=TOKENS["grid"],
            zerolinecolor=TOKENS["grid"],
            tickfont=dict(color=TOKENS["text_dim"] if "text_dim" in TOKENS else TOKENS["text_muted"])
        )
    )

def apply_theme(fig):
    """Applies the Bet Intel theme to an existing Plotly Figure."""
    fig.update_layout(**get_base_layout())
    return fig
