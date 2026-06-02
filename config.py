"""Configuration and operational constants for the dashboard."""

DATA_FILES = {
    "ingestion": ["ingestion_logs.csv", "ingestion_logs(1).csv"],
    "agent": ["agent_call_outcomes.csv", "agent_call_outcomes(1).csv"],
    "api": ["api_health_metrics.csv", "api_health_metrics(1).csv"],
    "alerts": ["system_alerts.json", "system_alerts(1).json"],
}

HARD_FAILURE_OUTCOMES = ["TOOL_ERROR", "TIMEOUT", "CALL_FAILED"]
BUSINESS_OUTCOMES = ["PATIENT_HANGUP", "NO_AVAILABILITY"]
SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

Z_SCORE_THRESHOLD = 2.0
PROVIDER_MIN_CALLS = 5

HIGH_CONTRAST_COLORS = [
    "#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa",
    "#22d3ee", "#fb923c", "#f472b6", "#4ade80", "#c084fc"
]
