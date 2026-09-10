"""serving-stack: the FastAPI service (week 2, CPU, tiny model).

This is the starter. GET /health is done for you and works as soon as the model
loads: treat it as the worked example. Your job is the two routes marked TODO.
Correctness before speed. The model runs on CPU this week; do not add a GPU.

Run it:
    uvicorn main:app --host 0.0.0.0 --port 8000

Model: Qwen/Qwen2.5-0.5B-Instruct (about 0.5B params; loads on CPU in seconds
once cached). The first ever load downloads weights; the prep-week verify-env
pass pre-seeded the Hugging Face cache, so a cached load is fast.
"""
from __future__ import annotations

import os
import time
import uuid

import torch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from transformers import AutoModelForCausalLM, AutoTokenizer

from schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    HealthResponse,
    ModelCard,
    ModelList,
    ResponseMessage,
    Usage,
)

MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
API_KEY = os.environ.get("API_KEY", "")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "256"))

if not API_KEY:
    print("WARNING: API_KEY is not set; /v1 endpoints are running unauthenticated")

app = FastAPI(title="serving-stack", version="wk2")
REQUESTS = Counter("serving_requests_total", "Total chat completion requests")
@app.middleware("http")
async def require_api_key(request: Request, call_next):
    if request.url.path.startswith("/v1/") and API_KEY:
        authorization = request.headers.get("Authorization", "")
        if authorization != f"Bearer {API_KEY}":
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"},
            )

    return await call_next(request)

# Load once at import time. CPU only this week.
print(f"loading {MODEL_ID} on cpu ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.float32)
model.to("cpu")
model.eval()
print("model ready")


# ---------------------------------------------------------------------------
# GET /health  -- DONE. This is the worked example. Copy its shape.
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness and readiness.

    Contract: returns 200 with {"status": "ok", "model": "<id>"} once the model
    is loaded. Kubernetes probes (week 4) and the agentic client's retry logic
    (weeks 4 to 6) call this. It must be cheap and must not run the model.
    """
    return HealthResponse(status="ok", model=MODEL_ID)


# ---------------------------------------------------------------------------
# GET /v1/models  -- TODO
# ---------------------------------------------------------------------------
@app.get("/v1/models", response_model=ModelList)
def list_models() -> ModelList:
    """List the served model id(s)."""
    return ModelList(
        data=[
            ModelCard(
                id=MODEL_ID,
                created=int(time.time()),
            )
        ]
    )

# ---------------------------------------------------------------------------
# POST /v1/chat/completions  -- TODO (non-streaming first)
# ---------------------------------------------------------------------------
@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(req: ChatCompletionRequest) -> ChatCompletionResponse:
    max_tokens = min(req.max_tokens, MAX_TOKENS)
    input_ids = tokenizer.apply_chat_template(
        [m.model_dump() for m in req.messages],
        add_generation_prompt=True,
        return_tensors="pt",
    )

    prompt_tokens = input_ids.shape[1]

    with torch.no_grad():
        out = model.generate(
            input_ids,
            max_new_tokens=max_tokens,
            do_sample=req.temperature > 0,
            temperature=req.temperature if req.temperature > 0 else None,
        )

    new_tokens = out[0][prompt_tokens:]
    completion_tokens = len(new_tokens)

    text = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True,
    )

    finish_reason = (
        "length"
        if completion_tokens >= max_tokens
        else "stop"
    )

    return ChatCompletionResponse(
        id="chatcmpl-" + uuid.uuid4().hex,
        created=int(time.time()),
        model=req.model,
        choices=[
            Choice(
                index=0,
                message=ResponseMessage(
                    role="assistant",
                    content=text,
                ),
                finish_reason=finish_reason,
            )
        ],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )   



# ---------------------------------------------------------------------------
# Streaming is a DELTA STEP, not required for the green check. See the README.
# When you add it: same route, if req.stream is True return a
# StreamingResponse of Server-Sent Events. Each event is
#   data: {chat.completion.chunk with choices[0].delta.content}\n\n
# and the stream ends with the literal line
#   data: [DONE]\n\n
# ---------------------------------------------------------------------------





@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
