"""
HealthCo Operations Command Center

Entry point for the Streamlit dashboard.

Run:
    streamlit run dashboard.py
"""

import plotly.express as px
import streamlit as st

from analysis import filter_scope
from config import HIGH_CONTRAST_COLORS
from data_loader import load_data
from styles import apply_theme
from views import (
    render_action_plan,
    render_agent_tab,
    render_api_alerts_tab,
    render_diagnostics_tab,
    render_header,
    render_ingestion_tab,
)


def main() -> None:
    """Run the Streamlit dashboard."""
    st.set_page_config(
        page_title="HealthCo Ops Command Center",
        page_icon="🏥",
        layout="wide",
    )

    apply_theme()

    px.defaults.color_discrete_sequence = HIGH_CONTRAST_COLORS
    px.defaults.template = "plotly_dark"

    ingestion, agent, api, alerts = load_data()

    st.sidebar.markdown("## ⚙️ Filters")
    customers = sorted(ingestion["customer_id"].dropna().unique().tolist())
    selected_customer = st.sidebar.selectbox("Customer Scope", ["All"] + customers)

    ingestion_view, agent_view, alerts_view = filter_scope(
        selected_customer,
        ingestion,
        agent,
        alerts,
    )

    render_header(ingestion_view, agent_view, api, alerts_view)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📥 Ingestion",
            "🤖 Agent Outcomes",
            "🚨 API & Alerts",
            "🔎 Diagnostics",
            "✅ Action Plan",
        ]
    )

    with tab1:
        render_ingestion_tab(ingestion, ingestion_view)

    with tab2:
        render_agent_tab(agent, agent_view)

    with tab3:
        render_api_alerts_tab(api, alerts, alerts_view, agent)

    with tab4:
        render_diagnostics_tab(ingestion, agent, api, alerts)

    with tab5:
        render_action_plan(ingestion, agent, api, alerts)


if __name__ == "__main__":
    main()
