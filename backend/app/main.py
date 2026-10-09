import json
import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from .guardrails import GuardrailViolation, enforce_action_policy, redact_pii, validate_prompt
from .providers import generate
from .router import choose_model

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("travel-concierge")

app = FastAPI(title="Secure Agentic Travel Concierge", version="1.0.0")


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2_000)
    requested_action: str | None = Field(default=None, max_length=120)
    confirmed: bool = False


class ChatResponse(BaseModel):
    trace_id: str
    route: str
    answer: str
    action_executed: bool


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "travel-concierge"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, response: Response) -> ChatResponse:
    trace_id = str(uuid.uuid4())
    started = time.perf_counter()
    try:
        safe_prompt = validate_prompt(request.prompt)
        enforce_action_policy(request.requested_action, request.confirmed)
        route = choose_model(safe_prompt)
        answer = redact_pii(await generate(safe_prompt, route.tier))
    except GuardrailViolation as exc:
        logger.warning(json.dumps({"trace_id": trace_id, "event": "blocked", "reason": str(exc)}))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(json.dumps({"trace_id": trace_id, "event": "provider_error"}))
        raise HTTPException(status_code=502, detail="Model provider unavailable") from exc

    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Trace-ID"] = trace_id
    logger.info(json.dumps({
        "trace_id": trace_id,
        "event": "chat_completed",
        "route": route.tier,
        "latency_ms": latency_ms,
        "action_executed": bool(request.requested_action and request.confirmed),
    }))
    return ChatResponse(
        trace_id=trace_id,
        route=route.tier,
        answer=answer,
        action_executed=bool(request.requested_action and request.confirmed),
    )

