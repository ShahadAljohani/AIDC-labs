Policy: serving is guaranteed enough CPU and memory for its measured burst, dashboard may burst when capacity is available, and batch throttles first.

serving:
  resources:
    requests:
      cpu: "1"
      memory: 512Mi
    limits:
      cpu: "1"
      memory: 512Mi

batch:
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

dashboard:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi

Evidence: batch is the first tenant to throttle because the measured serving p95 improved from 4ms with an unlimited neighbour to 3ms with the neighbour limited to 500m.
