import re

INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"developer\s+message",
    r"bypass\s+(the\s+)?guardrail",
    r"act\s+as\s+root",
)

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d -]{7,}\d)(?!\d)")
CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)")


class GuardrailViolation(ValueError):
    pass


def validate_prompt(prompt: str) -> str:
    normalized = " ".join(prompt.split())
    if not normalized:
        raise GuardrailViolation("Prompt cannot be empty")
    if len(normalized) > 2_000:
        raise GuardrailViolation("Prompt exceeds the 2,000-character limit")
    if any(re.search(pattern, normalized, re.I) for pattern in INJECTION_PATTERNS):
        raise GuardrailViolation("Potential prompt-injection attempt blocked")
    return redact_pii(normalized)


def redact_pii(text: str) -> str:
    text = EMAIL_RE.sub("[EMAIL_REDACTED]", text)
    text = PHONE_RE.sub("[PHONE_REDACTED]", text)
    return CARD_RE.sub("[PAYMENT_DATA_REDACTED]", text)


def enforce_action_policy(requested_action: str | None, confirmed: bool) -> None:
    if requested_action and not confirmed:
        raise GuardrailViolation("External actions require explicit user confirmation")

