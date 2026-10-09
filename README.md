# Secure Agentic Travel Concierge

Submission implementation for the LLMSecOps workshop. It demonstrates model routing, input/output guardrails, structured audit logging, prompt evaluation, model-quality tests, containerization, Kubernetes deployment, and CI/CD security gates.

## Architecture

`Browser -> frontend -> FastAPI /chat -> guardrails -> model router -> mock/Ollama/OpenAI provider -> output checks -> audit log`

The default `mock` provider requires no API key. It makes the repository reproducible in CI. Production providers are selected with environment variables.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5000
- Backend API: http://localhost:8080
- OpenAPI: http://localhost:8080/docs
- Health: http://localhost:8080/health

## Local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements-dev.txt
pytest backend/tests -q
uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
```

In another terminal:

```bash
python -m http.server 5000 --directory frontend
```

## Security and quality controls

- Maximum prompt length and strict request schema
- Prompt-injection pattern detection
- PII redaction for email, phone, and payment-card-like values
- Deny-by-default external action confirmation
- Complexity-based model routing
- Correlation IDs and structured JSON audit logs
- Unit and API tests
- Promptfoo policy and relevance checks
- DeepEval-ready evaluation test
- Dependency review, Bandit, pip-audit, and Trivy image scanning
- GitHub Actions build and test gates before image publication
- Non-root containers, read-only root filesystem, dropped Linux capabilities, and Kubernetes resource limits

## Environment variables

| Name | Purpose | Default |
|---|---|---|
| `MODEL_PROVIDER` | `mock`, `ollama`, or `openai` | `mock` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://host.docker.internal:11434` |
| `OLLAMA_MODEL_FAST` | Fast local model | `gemma2:2b` |
| `OLLAMA_MODEL_QUALITY` | Higher-quality local model | `llama3.1:8b` |
| `OPENAI_API_KEY` | OpenAI credential | unset |
| `LANGFUSE_PUBLIC_KEY` | Optional observability | unset |
| `LANGFUSE_SECRET_KEY` | Optional observability | unset |
| `LANGFUSE_HOST` | Optional Langfuse host | unset |

Never commit real keys. The image namespace is configured as `venk196`. Configure `DOCKERHUB_TOKEN` and any optional live-provider keys as GitHub Actions repository secrets.

## CI/CD flow

1. Pull request: lint, unit tests, API tests, Bandit, pip-audit, Promptfoo configuration validation.
2. Main branch: build backend and frontend images.
3. Scan both images with Trivy. Critical/high findings fail the workflow.
4. Authenticate to Docker Hub only after tests and scans pass.
5. Push immutable commit-SHA tags and `latest`.
6. Deploy using the Kubernetes manifests after an environment approval.
7. Verify `/health`, monitor logs/latency/error rate, and roll back to the previous immutable tag if needed.

## Workshop mapping

- llmapp01: `MODEL_PROVIDER=ollama`
- llmapp02: centralized provider configuration
- llmapp03: `choose_model()` routing
- llmapp04: `promptfoo/promptfooconfig.yaml`
- llmapp05: `deepeval/test_evaluation.py`
- llmapp06: structured audit logging
- llmapp07: optional Langfuse environment hooks
- llmapp08: `guardrails.py`
- llmapp09: Docker, Compose, Kubernetes, and GitHub Actions

