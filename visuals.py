"""Visualization helpers."""

import plotly.graph_objects as go
import streamlit as st


def pct(value: float) -> str:
    """Format a percentage."""
    return f"{value:.1f}%"


def style_fig(fig: go.Figure, height: int | None = None) -> go.Figure:
    """Apply shared high-contrast Plotly styling."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15,23,42,0)",
        plot_bgcolor="rgba(15,23,42,0.72)",
        font=dict(color="#f8fafc", size=13),
        title=dict(font=dict(color="#ffffff", size=19)),
        legend=dict(
            bgcolor="rgba(15,23,42,0)",
            bordercolor="rgba(125,211,252,0.25)",
            borderwidth=0,
            font=dict(color="#f8fafc", size=12),
        ),
        margin=dict(l=55, r=35, t=70, b=55),
        height=height,
    )

    fig.update_xaxes(
        title_font=dict(color="#f8fafc"),
        tickfont=dict(color="#cbd5e1"),
        gridcolor="rgba(148,163,184,0.20)",
        zerolinecolor="rgba(148,163,184,0.35)",
        linecolor="rgba(148,163,184,0.35)",
    )

    fig.update_yaxes(
        title_font=dict(color="#f8fafc"),
        tickfont=dict(color="#cbd5e1"),
        gridcolor="rgba(148,163,184,0.20)",
        zerolinecolor="rgba(148,163,184,0.35)",
        linecolor="rgba(148,163,184,0.35)",
    )

    fig.update_traces(textfont=dict(color="#ffffff"), selector=dict(type="pie"))

    return fig


def chart(fig: go.Figure, height: int | None = None) -> None:
    """Render a styled Plotly chart."""
    st.plotly_chart(style_fig(fig, height), use_container_width=True)


def table(df, max_rows: int = 15) -> None:
    """Render a dataframe using a custom high-contrast table style."""
    if df is None or df.empty:
        st.info("No records to display.")
        return

    display_df = df.head(max_rows).copy()
    html = display_df.to_html(index=False, classes="ops-table", escape=False)
    st.markdown(html, unsafe_allow_html=True)

    if len(df) > max_rows:
        st.caption(f"Showing first {max_rows} of {len(df)} rows.")
