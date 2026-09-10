****# Integration note: Shahad (v1, go-live)****

- ********base_url****** (client form, ends in `/v1` - paste into an OpenAI client):

`https://t12.aidc.nadir.sh/v1`

- ********service root****** (no `/v1` - the runbook's triage curls and `verify.sh`

build paths from this):

`https://t12.aidc.nadir.sh`

- ********model id:****** `Qwen/Qwen2.5-1.5B-Instruct-AWQ`

- ********auth:****** bearer key, handed over in person to the paired team's on-call

- ********modalities:****** text in, text out, tool calls per the OpenAI schema.

- ********example call:******

`curl -s https://t12.aidc.nadir.sh/v1/chat/completions -H "Authorization: Bearer REDACTED" -H 'Content-Type: application/json' -d '{"model":"Qwen/Qwen2.5-1.5B-Instruct-AWQ","messages":[{"role":"user","content":"hello from outside"}]}'`

- ********SLOs we publish:****** availability 99% over the window · TTFT p95 less than 500 ms

(tier 1) · error rate less than 1%

- ********limits, declared honestly:****** max_tokens clamp 512 · concurrency knee ~**16**

(from your wk-3 bench) · single GPU pod, no autoscaling

- ********on-call:****** t12 team · Slack #t12-oncall · response within 15 minutes during the window
