## Completing the lab: 

metrics history: 373.0 serving series in the store


outside-in posture verified for https://t12.aidc.nadir.sh serving Qwen/Qwen2.5-1.5B-Instruct-AWQ


GREEN CHECK: PASS


## Predict Questions:
Your endpoint goes through the pod's tunnel. Name the two things that can now take it down that have nothing to do with Kubernetes.
  > restarting on the host. the VM losing internet connectivity to Cloudflare's edge.cloudflared

The agentic cohort's client sets base_url to your URL and changes nothing else. What is the first request their framework will actually send: a chat completion, or something else? (Think about what their client does on startup.)
  > /v1/models

Your engine answers first tokens in tens of milliseconds on the pod. Your consumer reaches it through the tunnel from wherever they are. Which TTFT can you honestly publish, and measured from where?
  > The TTFT measured from outside, through the tunnel 
