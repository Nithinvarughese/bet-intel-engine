# Plotly Theme Configuration for Bet Intel — Indigo & Gold palette

TOKENS = {
    "bg_deep": "#080612",
    "surface_2": "rgba(32, 20, 60, 0.75)",
    "text_main": "#faf5ff",
    "text_muted": "#c4b5fd",
    "accent": "#f59e0b",
    "accent2": "#a78bfa",
    "grid": "rgba(255, 255, 255, 0.05)",
}

def get_base_layout():
    """Returns standard layout dictionary for all Plotly charts."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, Inter, sans-serif", color=TOKENS["text_muted"], size=12),
        margin=dict(t=40, b=40, l=40, r=40),
        hoverlabel=dict(
            bgcolor="#1e1040",
            font_size=13,
            font_family="Inter, sans-serif",
        ),
        xaxis=dict(
            gridcolor=TOKENS["grid"],
            zerolinecolor=TOKENS["grid"],
            tickfont=dict(color=TOKENS["text_muted"]),
        ),
        yaxis=dict(
            gridcolor=TOKENS["grid"],
            zerolinecolor=TOKENS["grid"],
            tickfont=dict(color=TOKENS["text_muted"]),
        ),
    )


def apply_theme(fig):
    """Applies the Bet Intel Indigo & Gold theme to an existing Plotly Figure."""
    fig.update_layout(**get_base_layout())
    return fig
