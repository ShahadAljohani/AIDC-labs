from __future__ import annotations

import os
import time
import uuid

from fastapi import FastAPI

from schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    HealthResponse,
    ModelList,
    ModelCard,
    Choice,
    ResponseMessage,
    Usage,
)

MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
MODEL_BACKEND = os.environ.get("MODEL_BACKEND", "transformers")

app = FastAPI(title="serving-stack", version="wk4")

if MODEL_BACKEND == "echo":
    tokenizer = None
    model = None
else:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"loading {MODEL_ID} on cpu ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32,
    )
    model.to("cpu")
    model.eval()
    print("model ready")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model=MODEL_ID)


@app.get("/v1/models", response_model=ModelList)
def list_models() -> ModelList:
    return ModelList(
        data=[ModelCard(id=MODEL_ID, created=int(time.time()))]
    )


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(req: ChatCompletionRequest) -> ChatCompletionResponse:

    if MODEL_BACKEND == "echo":
        content = " ".join(
            m.content
            for m in req.messages
            if getattr(m, "role", "") == "user"
        )

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex}",
            object="chat.completion",
            created=int(time.time()),
            model=req.model,
            choices=[
                Choice(
                    index=0,
                    message=ResponseMessage(
                        role="assistant",
                        content=content,
                    ),
                    finish_reason="stop",
                )
            ],
            usage=Usage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )

    messages_payload = [m.model_dump() for m in req.messages]

    input_ids = tokenizer.apply_chat_template(
        messages_payload,
        add_generation_prompt=True,
        return_tensors="pt",
    )

    input_ids = input_ids["input_ids"]
    prompt_tokens = input_ids.shape[1]

    with torch.no_grad():
        if req.temperature > 0.0:
            out = model.generate(
                input_ids,
                max_new_tokens=req.max_tokens,
                do_sample=True,
                temperature=req.temperature,
            )
        else:
            out = model.generate(
                input_ids,
                max_new_tokens=req.max_tokens,
                do_sample=False,
            )

    new_tokens = out[0][prompt_tokens:]
    completion_tokens = len(new_tokens)
    text = tokenizer.decode(new_tokens, skip_special_tokens=True)

    finish_reason = (
        "length" if completion_tokens >= req.max_tokens else "stop"
    )

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        object="chat.completion",
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
