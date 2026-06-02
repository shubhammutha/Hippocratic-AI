# FINDINGS

## 1. Platform API degradation is the top priority

The dashboard identifies circuit breaker OPEN windows and overlays them directly with hourly agent hard failures and average API error rate.

How it was found:
- Circuit breaker window detection
- API error-rate trend
- dedicated overlay chart: circuit breaker windows + agent hard failures + API error rate
- hourly z-score anomaly detection

Recommendation:
Investigate the API degradation window first. Review API logs, dependency health, retry behavior, capacity saturation, and circuit breaker thresholds.

---

## 2. Customer data-quality issues are visible in ingestion and validation patterns

The ingestion view shows which customers have elevated ingestion failures and which validation layers are most problematic.

How it was found:
- daily ingestion outcome trend
- ingestion failure rate by customer
- validation-layer heatmap
- ingestion risk table

Recommendation:
Escalate the highest-risk customer to the integration team. Review schema validation, API contract failures, business-rule failures, and AI semantic validation outputs.

---

## 3. Provider-level hard failure outliers require investigation

The dashboard separates hard platform failures from business outcomes and uses z-score outlier detection to flag providers with unusually high hard failure rates.

How it was found:
- provider-level hard failure rate
- minimum call threshold
- z-score detection

Recommendation:
Review provider scheduling configuration, routing, tool integration responses, and recurring error codes.

---

## 4. Same customer / same hour correlation shows possible upstream-to-downstream impact

The diagnostics tab correlates ingestion failures and agent hard failures for the same customer in the same hourly time window.

How it was found:
- same customer / same hour correlation table
- customer-hour scatter plot
- integrated customer priority score

Recommendation:
When both upstream ingestion failures and downstream agent hard failures occur for the same customer/time window, investigate ingestion logs first, then compare against agent call failures.

---

## On-Call Priority

1. Stabilize Platform API and review circuit breaker windows.
2. Escalate the highest-priority customer from the integrated risk score.
3. Investigate provider hard-failure outliers.
4. Review validation-layer failures and AI blocker findings.
5. Add proactive alerts for validation spikes, provider outliers, and customer-hour combined issues.
