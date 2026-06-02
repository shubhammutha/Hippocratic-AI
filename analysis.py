"""Analysis functions for operational monitoring."""

from typing import Dict, Tuple
import pandas as pd

from config import PROVIDER_MIN_CALLS, Z_SCORE_THRESHOLD


def filter_scope(
    customer: str,
    ingestion: pd.DataFrame,
    agent: pd.DataFrame,
    alerts: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Apply customer filter to customer-scoped datasets."""
    if customer == "All":
        return ingestion, agent, alerts

    return (
        ingestion[ingestion["customer_id"] == customer],
        agent[agent["customer_id"] == customer],
        alerts[alerts["customer_id"] == customer],
    )


def minutes_from_snapshots(open_count: int) -> int:
    """API health snapshots are sampled every five minutes."""
    return int(open_count * 5)


def get_breaker_windows(api: pd.DataFrame) -> pd.DataFrame:
    """Identify continuous circuit breaker OPEN windows."""
    api_sorted = api.sort_values("timestamp").copy()
    windows = []
    start = None
    previous_timestamp = None
    open_snapshot_count = 0

    for row in api_sorted.itertuples():
        if row.is_breaker_open and start is None:
            start = row.timestamp
            open_snapshot_count = 1
        elif row.is_breaker_open:
            open_snapshot_count += 1
        elif start is not None:
            windows.append(
                {
                    "start": start,
                    "end": previous_timestamp,
                    "open_snapshots": open_snapshot_count,
                    "duration_min": minutes_from_snapshots(open_snapshot_count),
                }
            )
            start = None
            open_snapshot_count = 0

        previous_timestamp = row.timestamp

    if start is not None:
        windows.append(
            {
                "start": start,
                "end": previous_timestamp,
                "open_snapshots": open_snapshot_count,
                "duration_min": minutes_from_snapshots(open_snapshot_count),
            }
        )

    if not windows:
        return pd.DataFrame(columns=["start", "end", "open_snapshots", "duration_min"])

    return pd.DataFrame(windows).sort_values("duration_min", ascending=False)


def customer_ingestion_risk(ingestion: pd.DataFrame) -> pd.DataFrame:
    """Customer-level ingestion failure risk."""
    group_columns = {"batches": ("customer_id", "count"), "failed_batches": ("is_failure", "sum")}
    optional_aggs = {}
    if "failed_records" in ingestion.columns:
        optional_aggs["avg_failed_records"] = ("failed_records", "mean")
    if "processing_time_ms" in ingestion.columns:
        optional_aggs["avg_processing_ms"] = ("processing_time_ms", "mean")

    result = ingestion.groupby("customer_id").agg(**group_columns, **optional_aggs).reset_index()
    result["failure_rate_pct"] = result["failed_batches"] / result["batches"] * 100
    return result.sort_values("failure_rate_pct", ascending=False)


def customer_agent_risk(agent: pd.DataFrame) -> pd.DataFrame:
    """Customer-level agent hard failure risk."""
    aggs = {
        "calls": ("customer_id", "count"),
        "hard_failures": ("is_hard_failure", "sum"),
    }
    if "api_latency_ms" in agent.columns:
        aggs["avg_latency_ms"] = ("api_latency_ms", "mean")
        aggs["p95_latency_ms"] = ("api_latency_ms", lambda s: s.quantile(0.95))

    result = agent.groupby("customer_id").agg(**aggs).reset_index()
    result["hard_failure_rate_pct"] = result["hard_failures"] / result["calls"] * 100
    return result.sort_values("hard_failure_rate_pct", ascending=False)


def provider_outliers(agent: pd.DataFrame) -> pd.DataFrame:
    """Provider-level hard failure outliers using z-score."""
    if "provider_id" not in agent.columns:
        return pd.DataFrame()

    aggs = {
        "calls": ("provider_id", "count"),
        "hard_failures": ("is_hard_failure", "sum"),
    }
    if "api_latency_ms" in agent.columns:
        aggs["avg_latency_ms"] = ("api_latency_ms", "mean")

    result = agent.groupby("provider_id").agg(**aggs).reset_index()
    result["hard_failure_rate_pct"] = result["hard_failures"] / result["calls"] * 100
    result = result[result["calls"] >= PROVIDER_MIN_CALLS].copy()

    std = result["hard_failure_rate_pct"].std()
    if std and std != 0:
        result["z_score"] = (result["hard_failure_rate_pct"] - result["hard_failure_rate_pct"].mean()) / std
    else:
        result["z_score"] = 0

    result["is_outlier"] = result["z_score"] > Z_SCORE_THRESHOLD
    return result.sort_values("z_score", ascending=False)


def hourly_system_correlation(
    ingestion: pd.DataFrame,
    agent: pd.DataFrame,
    api: pd.DataFrame,
    alerts: pd.DataFrame,
) -> pd.DataFrame:
    """Hourly cross-system signals with z-score anomaly flags."""
    ingestion_hourly = (
        ingestion.set_index("timestamp")
        .resample("h")["is_failure"]
        .sum()
        .reset_index(name="ingestion_failures")
    )

    agent_hourly = (
        agent.set_index("timestamp")
        .resample("h")["is_hard_failure"]
        .sum()
        .reset_index(name="agent_hard_failures")
    )

    alerts_hourly = (
        alerts.set_index("timestamp")
        .resample("h")
        .size()
        .reset_index(name="alert_count")
    )

    api_aggs = {
        "avg_api_error_rate": ("error_rate_pct", "mean"),
        "breaker_open_count": ("is_breaker_open", "sum"),
    }
    if "p99_latency_ms" in api.columns:
        api_aggs["avg_p99_latency_ms"] = ("p99_latency_ms", "mean")

    api_hourly = (
        api.set_index("timestamp")
        .resample("h")
        .agg(**api_aggs)
        .reset_index()
    )

    hourly = ingestion_hourly.merge(agent_hourly, on="timestamp", how="outer")
    hourly = hourly.merge(alerts_hourly, on="timestamp", how="outer")
    hourly = hourly.merge(api_hourly, on="timestamp", how="outer")
    hourly = hourly.fillna(0)

    metrics = [
        "ingestion_failures",
        "agent_hard_failures",
        "alert_count",
        "avg_api_error_rate",
        "breaker_open_count",
    ]
    if "avg_p99_latency_ms" in hourly.columns:
        metrics.append("avg_p99_latency_ms")

    for col in metrics:
        std = hourly[col].std()
        hourly[f"{col}_z"] = 0 if not std else (hourly[col] - hourly[col].mean()) / std

    hourly["anomaly_score"] = hourly[[f"{col}_z" for col in metrics]].abs().max(axis=1)
    hourly["anomaly_flag"] = hourly["anomaly_score"] > Z_SCORE_THRESHOLD
    return hourly.sort_values("timestamp")


def customer_hour_correlation(ingestion: pd.DataFrame, agent: pd.DataFrame) -> pd.DataFrame:
    """Same customer/same hour correlation between ingestion failures and agent failures."""
    ingestion_hour = (
        ingestion.set_index("timestamp")
        .groupby([pd.Grouper(freq="h"), "customer_id"])["is_failure"]
        .sum()
        .reset_index(name="ingestion_failures")
    )

    agent_hour = (
        agent.set_index("timestamp")
        .groupby([pd.Grouper(freq="h"), "customer_id"])["is_hard_failure"]
        .sum()
        .reset_index(name="agent_hard_failures")
    )

    result = ingestion_hour.merge(agent_hour, on=["timestamp", "customer_id"], how="outer").fillna(0)
    result["combined_issue_score"] = result["ingestion_failures"] + result["agent_hard_failures"]
    return result.sort_values("combined_issue_score", ascending=False)


def integrated_risk_score(
    ingestion: pd.DataFrame,
    agent: pd.DataFrame,
    alerts: pd.DataFrame,
) -> pd.DataFrame:
    """Integrated customer priority score."""
    ingestion_risk = customer_ingestion_risk(ingestion)[["customer_id", "failure_rate_pct", "failed_batches"]]
    agent_risk = customer_agent_risk(agent)[["customer_id", "hard_failure_rate_pct", "hard_failures"]]

    alert_risk = (
        alerts.dropna(subset=["customer_id"])
        .groupby("customer_id")
        .agg(
            total_alerts=("alert_id", "count"),
            unresolved_alerts=("resolved", lambda s: (~s).sum()),
            critical_alerts=("severity", lambda s: (s == "CRITICAL").sum()),
        )
        .reset_index()
    )

    result = ingestion_risk.merge(agent_risk, on="customer_id", how="outer")
    result = result.merge(alert_risk, on="customer_id", how="outer")
    result = result.fillna(0)

    result["priority_score"] = (
        result["failure_rate_pct"]
        + result["hard_failure_rate_pct"]
        + result["critical_alerts"] * 4
        + result["unresolved_alerts"] * 2
    ).round(2)

    return result.sort_values("priority_score", ascending=False)


def outcome_success_summary(agent: pd.DataFrame) -> Dict[str, float]:
    """Summarize agent outcomes."""
    total = len(agent)
    if total == 0:
        return {"scheduled_rate": 0, "hard_failure_rate": 0, "business_outcome_rate": 0}

    return {
        "scheduled_rate": agent["outcome"].eq("SCHEDULED").sum() / total * 100,
        "hard_failure_rate": agent["is_hard_failure"].sum() / total * 100,
        "business_outcome_rate": agent["is_business_outcome"].sum() / total * 100,
    }
