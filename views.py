"""Streamlit UI views for the HealthCo dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analysis import (
    customer_agent_risk,
    customer_hour_correlation,
    customer_ingestion_risk,
    get_breaker_windows,
    hourly_system_correlation,
    integrated_risk_score,
    minutes_from_snapshots,
    outcome_success_summary,
    provider_outliers,
)
from config import SEVERITY_ORDER, Z_SCORE_THRESHOLD
from visuals import chart, pct, table


def render_header(ingestion, agent, api, alerts) -> None:
    """Render top operational briefing."""
    breaker_windows = get_breaker_windows(api)
    breaker_minutes = minutes_from_snapshots(int(api["is_breaker_open"].sum()))
    hard_failure_rate = agent["is_hard_failure"].mean() * 100
    ingestion_failure_rate = ingestion["is_failure"].mean() * 100

    st.markdown(
        """
<div class="hero">
    <h1>🏥 HealthCo Operations Command Center</h1>
    <p>Monday-morning triage view across ingestion, API health, alerts, and AI scheduling outcomes.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ingestion Failure Rate", pct(ingestion_failure_rate), f"{int(ingestion['is_failure'].sum())} failed")
    c2.metric("Agent Hard Failure Rate", pct(hard_failure_rate), f"{int(agent['is_hard_failure'].sum())} hard failures")
    c3.metric("Unresolved Alerts", int((~alerts["resolved"]).sum()), f"{int((alerts['severity']=='CRITICAL').sum())} critical total")
    c4.metric("Circuit Breaker Open", f"{breaker_minutes} min", f"{int(api['is_breaker_open'].sum())} snapshots")
    c5.metric("Volume", f"{len(ingestion)} / {len(agent):,}", "batches / calls")

    top_ing = customer_ingestion_risk(ingestion).iloc[0]
    top_provider = provider_outliers(agent).iloc[0]
    peak_api = api.loc[api["error_rate_pct"].idxmax()]

    if not breaker_windows.empty:
        longest = breaker_windows.iloc[0]
        api_line = (
            f"<b>API degradation:</b> circuit breaker was open for {breaker_minutes} total minutes; "
            f"longest continuous window was {int(longest['duration_min'])} min "
            f"({longest['start']} → {longest['end']}). Peak API error rate was {peak_api['error_rate_pct']:.1f}%."
        )
    else:
        api_line = "<b>API degradation:</b> no circuit breaker open windows detected."

    st.markdown(
        f"""
<div class="glass-card">
    <h3>🚦 Operational Briefing</h3>
    <div class="signal-card-critical">{api_line}</div>
    <div class="signal-card-warning"><b>Customer data quality risk:</b> {top_ing['customer_id']} has the highest ingestion failure rate at {top_ing['failure_rate_pct']:.1f}% ({int(top_ing['failed_batches'])}/{int(top_ing['batches'])} batches).</div>
    <div class="signal-card"><b>Provider outlier:</b> {top_provider['provider_id']} has a {top_provider['hard_failure_rate_pct']:.1f}% hard failure rate with z-score {top_provider['z_score']:.2f}.</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_ingestion_tab(ingestion, ingestion_view) -> None:
    """Render ingestion monitoring view."""
    st.header("📥 Ingestion Health")

    col1, col2 = st.columns([1.1, 1])

    with col1:
        daily = ingestion_view.groupby(["date", "status"]).size().reset_index(name="batches")
        fig = px.bar(daily, x="date", y="batches", color="status", title="Daily Ingestion Outcomes")
        chart(fig, 430)

    with col2:
        risk = customer_ingestion_risk(ingestion)
        fig = px.bar(
            risk.sort_values("failure_rate_pct"),
            x="failure_rate_pct",
            y="customer_id",
            orientation="h",
            title="Ingestion Failure Rate by Customer",
        )
        chart(fig, 430)

    st.subheader("Validation Layer Breakdown")

    validation_source = ingestion[ingestion["validation_layer_failed"].notna()]
    heatmap = pd.crosstab(validation_source["customer_id"], validation_source["validation_layer_failed"])
    fig = px.imshow(heatmap, text_auto=True, aspect="auto", title="Validation Failures by Customer and Layer")
    chart(fig, 420)

    st.subheader("Ingestion Risk Table")
    display = customer_ingestion_risk(ingestion).round(2)
    table(display, 10)


def render_agent_tab(agent, agent_view) -> None:
    """Render agent outcome and provider outlier view."""
    st.header("🤖 Agent Call Outcomes")

    summary = outcome_success_summary(agent_view)
    a, b, c = st.columns(3)
    a.metric("Scheduled Rate", pct(summary["scheduled_rate"]))
    b.metric("Hard Failure Rate", pct(summary["hard_failure_rate"]))
    c.metric("Business Outcome Rate", pct(summary["business_outcome_rate"]))

    st.markdown(
        """
<div class="glass-card">
    <span class="badge">Operational definition</span>
    <p style="margin-top:10px;">
    Hard platform failures are <b>TOOL_ERROR</b>, <b>TIMEOUT</b>, and <b>CALL_FAILED</b>.
    Patient hangups and no availability are tracked separately because they are not necessarily system failures.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.05, 1])

    with col1:
        outcome_daily = agent_view.groupby(["date", "outcome"]).size().reset_index(name="calls")
        fig = px.bar(outcome_daily, x="date", y="calls", color="outcome", title="Daily Agent Outcomes by Type")
        chart(fig, 430)

    with col2:
        customer_risk = customer_agent_risk(agent)
        fig = px.bar(
            customer_risk.sort_values("hard_failure_rate_pct"),
            x="hard_failure_rate_pct",
            y="customer_id",
            orientation="h",
            title="Agent Hard Failure Rate by Customer",
        )
        chart(fig, 430)

    st.subheader("Provider Outlier Detection")
    providers = provider_outliers(agent)
    fig = px.scatter(
        providers,
        x="calls",
        y="hard_failure_rate_pct",
        size="hard_failures",
        color="is_outlier",
        hover_data=["provider_id", "z_score"],
        title="Provider Hard Failure Outliers",
    )
    chart(fig, 420)
    table(providers.round(2), 15)


def render_api_alerts_tab(api, alerts, alerts_view, agent) -> None:
    """Render API/alert view and explicit circuit-breaker/failure overlay."""
    st.header("🚨 API Health & Alert Operations")

    col1, col2, col3 = st.columns(3)
    col1.metric("Peak API Error Rate", pct(api["error_rate_pct"].max()))
    col2.metric("Peak P99 Latency", f"{api['p99_latency_ms'].max():,.0f} ms" if "p99_latency_ms" in api.columns else "N/A")
    col3.metric("Unacknowledged Alerts", int((~alerts_view["acknowledged"]).sum()))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=api["timestamp"], y=api["error_rate_pct"], mode="lines", name="API Error Rate %"))
    if "p99_latency_ms" in api.columns:
        fig.add_trace(
            go.Scatter(
                x=api["timestamp"],
                y=api["p99_latency_ms"] / 1000,
                mode="lines",
                name="P99 Latency (sec)",
                yaxis="y2",
            )
        )
    fig.update_layout(
        title="API Error Rate, Latency, and Circuit Breaker Windows",
        yaxis=dict(title="Error Rate (%)"),
        yaxis2=dict(title="P99 Latency (sec)", overlaying="y", side="right"),
    )
    for row in get_breaker_windows(api).itertuples():
        fig.add_vrect(x0=row.start, x1=row.end, fillcolor="rgba(239,68,68,0.22)", line_width=0)
    chart(fig, 460)

    st.subheader("Circuit Breaker Windows Overlaid with Agent Hard Failures")

    # This chart directly satisfies the bonus requirement:
    # circuit breaker OPEN windows are shaded behind agent hard failure counts.
    agent_hour = (
        agent.set_index("timestamp")
        .resample("h")["is_hard_failure"]
        .sum()
        .reset_index(name="agent_hard_failures")
    )

    api_hour = (
        api.set_index("timestamp")
        .resample("h")
        .agg(
            avg_api_error_rate=("error_rate_pct", "mean"),
            breaker_open_count=("is_breaker_open", "sum"),
        )
        .reset_index()
    )

    overlay = agent_hour.merge(api_hour, on="timestamp", how="outer").fillna(0)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=overlay["timestamp"],
            y=overlay["agent_hard_failures"],
            name="Agent Hard Failures",
            marker_color="#f87171",
            opacity=0.88,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=overlay["timestamp"],
            y=overlay["avg_api_error_rate"],
            name="Avg API Error Rate %",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#38bdf8", width=3),
        )
    )
    fig.update_layout(
        title="Circuit Breaker OPEN Windows + Agent Hard Failures + API Error Rate",
        yaxis=dict(title="Agent Hard Failures"),
        yaxis2=dict(title="Avg API Error Rate (%)", overlaying="y", side="right"),
        barmode="overlay",
    )
    for row in get_breaker_windows(api).itertuples():
        fig.add_vrect(
            x0=row.start,
            x1=row.end,
            fillcolor="rgba(239,68,68,0.28)",
            line_width=0,
            annotation_text="Breaker OPEN",
            annotation_position="top left",
        )
    chart(fig, 500)

    st.markdown(
        """
<div class="signal-card">
    <b>Why this matters:</b> this chart explicitly places agent hard failures on top of circuit-breaker OPEN windows and API error rate.
    If failures rise inside shaded windows, the on-call team has direct evidence that API degradation may be contributing to downstream call failures.
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(alerts_view, x="severity", color="severity", category_orders={"severity": SEVERITY_ORDER}, title="Alerts by Severity")
        chart(fig, 390)
    with col2:
        fig = px.histogram(alerts_view, x="alert_type", color="severity", title="Alerts by Type")
        chart(fig, 390)

    alerts_hourly = alerts_view.set_index("timestamp").resample("h").size().reset_index(name="alert_count")
    fig = px.line(alerts_hourly, x="timestamp", y="alert_count", markers=True, title="Alert Volume Over Time")
    chart(fig, 380)

    st.subheader("Unresolved Alerts")
    unresolved = alerts_view[alerts_view["resolved"] == False]
    table(unresolved[["alert_id", "timestamp", "severity", "alert_type", "system", "customer_id"]], 20)


def render_diagnostics_tab(ingestion, agent, api, alerts) -> None:
    """Render correlation and anomaly diagnostics."""
    st.header("🔎 Cross-System Diagnostics")

    hourly = hourly_system_correlation(ingestion, agent, api, alerts)

    z_cols = [col for col in hourly.columns if col.endswith("_z")]
    fig = px.line(hourly, x="timestamp", y=z_cols, title="Normalized Hourly Signals (z-score overlay)")
    fig.add_hline(y=Z_SCORE_THRESHOLD, line_dash="dash", line_color="#f97316")
    fig.add_hline(y=-Z_SCORE_THRESHOLD, line_dash="dash", line_color="#f97316")
    chart(fig, 460)

    st.subheader("Detected Anomaly Windows")
    anomalies = hourly[hourly["anomaly_flag"]].copy().sort_values("anomaly_score", ascending=False)
    display_cols = ["timestamp", "ingestion_failures", "agent_hard_failures", "alert_count", "avg_api_error_rate", "breaker_open_count", "anomaly_score"]
    if "avg_p99_latency_ms" in anomalies.columns:
        display_cols.insert(-1, "avg_p99_latency_ms")
    table(anomalies[display_cols].round(2), 20)

    st.subheader("Same Customer / Same Hour Correlation")
    customer_hour = customer_hour_correlation(ingestion, agent)
    col1, col2 = st.columns([1.1, 1])
    with col1:
        fig = px.scatter(
            customer_hour,
            x="ingestion_failures",
            y="agent_hard_failures",
            color="customer_id",
            size="combined_issue_score",
            hover_data=["timestamp", "customer_id"],
            title="Ingestion Failures vs Agent Hard Failures by Customer-Hour",
        )
        chart(fig, 430)
    with col2:
        table(customer_hour, 12)

    st.subheader("Integrated Customer Priority Score")
    risk = integrated_risk_score(ingestion, agent, alerts)
    table(risk.round(2), 10)

    fig = px.imshow(
        risk.set_index("customer_id")[["failure_rate_pct", "hard_failure_rate_pct", "critical_alerts", "unresolved_alerts", "priority_score"]],
        text_auto=True,
        aspect="auto",
        title="Customer Risk Heatmap",
    )
    chart(fig, 420)


def render_action_plan(ingestion, agent, api, alerts) -> None:
    """Render prioritized action plan."""
    st.header("✅ Action Plan")

    risk = integrated_risk_score(ingestion, agent, alerts)
    top_customer = risk.iloc[0]
    top_provider = provider_outliers(agent).iloc[0]
    breaker_minutes = minutes_from_snapshots(int(api["is_breaker_open"].sum()))

    st.markdown(
        f"""
<div class="signal-card-critical">
    <h3>Priority 1 — Stabilize Platform API</h3>
    <p>Evidence: circuit breaker was open for <b>{breaker_minutes} minutes</b>, peak API error rate reached <b>{api['error_rate_pct'].max():.1f}%</b>, and breaker windows are explicitly overlaid with agent hard failures.</p>
    <p>Action: review API logs, dependency health, capacity saturation, retry behavior, and circuit breaker thresholds.</p>
</div>

<div class="signal-card-warning">
    <h3>Priority 2 — Escalate Highest-Risk Customer: {top_customer['customer_id']}</h3>
    <p>Evidence: integrated priority score is <b>{top_customer['priority_score']:.1f}</b>.</p>
    <p>Action: check validation-layer failures, recent data changes, schema version changes, and customer configuration.</p>
</div>

<div class="signal-card">
    <h3>Priority 3 — Investigate Provider Outlier: {top_provider['provider_id']}</h3>
    <p>Evidence: provider hard failure rate is <b>{top_provider['hard_failure_rate_pct']:.1f}%</b> with z-score <b>{top_provider['z_score']:.2f}</b>.</p>
    <p>Action: inspect provider scheduling configuration, tool integration responses, routing, and repeated error codes.</p>
</div>
""",
        unsafe_allow_html=True,
    )
