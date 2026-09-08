# CPU Resource Policy

Serving is guaranteed enough CPU to cover its measured burst, dashboard may burst when CPU is available, and batch throttles first when the node is under pressure.

## Serving — Guaranteed

```yaml
resources:
  requests:
    cpu: "2"
    memory: "256Mi"
  limits:
    cpu: "2"
    memory: "256Mi"
```

## Batch — Burstable

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

## Dashboard — BestEffort

```yaml
resources: {}
```

Batch is the loser by design: the unlimited-neighbour p95 was **UNLIMITED_P95**, while the 500m-limited neighbour p95 was **LIMITED_P95**, showing that CPU throttling makes serving latency more predictable.
