from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    tier: str
    reason: str


def choose_model(prompt: str) -> RouteDecision:
    complex_markers = ("compare", "optimize", "multi-city", "constraint", "risk", "evaluate")
    score = len(prompt.split()) + 20 * sum(marker in prompt.lower() for marker in complex_markers)
    if score >= 45:
        return RouteDecision("quality", "Complex or constraint-heavy travel request")
    return RouteDecision("fast", "Routine travel request")

