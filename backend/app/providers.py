import os

import httpx


def _mock_response(prompt: str, tier: str) -> str:
    return (
        f"[{tier} route] Suggested next step: confirm destination, dates, budget, and traveller "
        f"preferences before booking. I received: {prompt[:240]}"
    )


async def generate(prompt: str, tier: str) -> str:
    provider = os.getenv("MODEL_PROVIDER", "mock").lower()
    if provider == "mock":
        return _mock_response(prompt, tier)
    if provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL_QUALITY" if tier == "quality" else "OLLAMA_MODEL_FAST")
        if not model:
            model = "llama3.1:8b" if tier == "quality" else "gemma2:2b"
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]
    raise RuntimeError(f"Unsupported MODEL_PROVIDER: {provider}")

