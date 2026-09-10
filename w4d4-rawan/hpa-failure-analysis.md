1. The CPU-based HPA fails for the real vLLM engine because the workload is GPU-bound. During load, the vLLM pod used only about 68m CPU, which is very low compared with its 4-CPU request. A 50% CPU target could therefore keep only one replica even while requests are waiting.

2. I would scale using vllm_num_requests_waiting because it directly shows when requests are queued and the engine cannot serve them immediately. This better represents the pressure on our inference workload than CPU usage.

3. I would start with a target of about 2 waiting requests per replica. I would tune that target by watching queue depth, p95 request latency, GPU utilization, and whether replicas scale early enough to prevent long waits.
