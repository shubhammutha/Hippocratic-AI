# HealthCo Operations Command Center

## Overview

This is a structured Streamlit dashboard for the HealthCo Operations Analyst technical assessment.

The dashboard analyzes all four provided operational datasets:

- `ingestion_logs.csv`
- `agent_call_outcomes.csv`
- `system_alerts.json`
- `api_health_metrics.csv`

It helps an on-call analyst understand:

- ingestion health
- validation-layer failure patterns
- AI agent outcome trends
- true platform hard failures
- provider-level outliers
- API degradation and circuit breaker windows
- alert severity/type trends
- same customer / same hour cross-system correlation
- prioritized on-call actions

## How to Run

Install dependencies:

```bash
pip install streamlit pandas plotly
```

Run the dashboard:

```bash
streamlit run dashboard.py
```

## Required File Layout

Keep these files in the same folder:

```text
dashboard.py
config.py
data_loader.py
analysis.py
visuals.py
styles.py
views.py
ingestion_logs.csv
agent_call_outcomes.csv
api_health_metrics.csv
system_alerts.json
README.md
FINDINGS.md
```

## Code Quality Structure

The project is intentionally split into modules:

| File | Purpose |
|---|---|
| `dashboard.py` | Streamlit app entry point |
| `config.py` | Constants, failure definitions, color palette, thresholds |
| `data_loader.py` | Data loading, timestamp conversion, helper columns |
| `analysis.py` | Operational calculations, anomaly detection, correlations |
| `visuals.py` | Chart/table rendering helpers |
| `styles.py` | Dashboard theme |
| `views.py` | Streamlit page sections/tabs |

This makes the code easier to review, test, and extend.

## Operational Definitions

Hard platform failures:

- `TOOL_ERROR`
- `TIMEOUT`
- `CALL_FAILED`

Business outcomes, not counted as platform failures:

- `PATIENT_HANGUP`
- `NO_AVAILABILITY`

##  Features

### Circuit Breaker Overlaid with Failures

The **API & Alerts** tab includes a dedicated chart:

> Circuit Breaker OPEN Windows + Agent Hard Failures + API Error Rate

It overlays:

- shaded circuit breaker OPEN windows
- hourly agent hard failures
- average API error rate

This directly satisfies the circuit-breaker overlay bonus requirement.

### Anomaly Detection

The **Diagnostics** tab uses z-score anomaly detection across hourly signals:

- ingestion failures
- agent hard failures
- alert count
- API error rate
- P99 latency when available
- circuit breaker open count

### Cross-System Correlation

The dashboard includes:

- hourly cross-system z-score overlay
- same customer / same hour ingestion-to-agent correlation
- integrated customer priority score

## Deliverables

- `dashboard.py` and supporting modules
- `README.md`
- `FINDINGS.md`
