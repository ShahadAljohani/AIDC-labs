# Service report

Team: Shahad

Use case: AI model serving / conversational inference

Service and model: team-serving / Qwen/Qwen2.5-1.5B-Instruct-AWQ

Measured requests or tasks: 10 chat completion requests

Indicator and unit: p95 time to first token (TTFT), seconds

SLO target and window: p95 TTFT < 1.0 second over a 5-minute window

Measurement start and end: 2026-09-14 11:52 UTC to 2026-09-14 11:52 UTC

Workload: 10 authenticated chat completion requests with max_tokens=8 and prompt "ping"

Observed result and sample count: p95 TTFT approximately 0.039 seconds; 10 requests generated

Evidence: Grafana service alert measurement and notification-evidence.jsonl

Conclusion: met

Limitations: The measurement represents a short artificial workload and a single 5-minute observation window; it does not establish sustained production performance.

Follow-up action: Repeat the measurement under a longer and more representative workload before treating the result as a production-level SLO assessment.

## Measurement query

```promql
histogram_quantile(0.95,
  sum by (le) (
    rate(vllm:time_to_first_token_seconds_bucket{job="serving"}[5m])
  )
)
```

Evaluation: Instant query using a 5-minute rate window.

The measurement is taken from the vLLM Prometheus metrics for the serving service. It measures time to first token and excludes other latency components such as time after the first token and end-to-end completion latency.

## Service alert

Condition and unit: p95 TTFT > 1.0 second

Evaluation interval: 1 minute

Pending period: 1 minute

Relationship to the SLO: The alert condition detects when p95 TTFT exceeds the SLO target.

First response to a notification: Check the serving service, Prometheus metrics, recent request traffic, and Grafana alert state.

## Notification test

Firing received at: 2026-09-14 11:48:20 UTC

Resolved received at: 2026-09-14 11:49:00 UTC

What the test establishes: The notification test established that the Grafana alerting path successfully delivered both firing and naturally resolved notifications to the Lab inbox webhook.
