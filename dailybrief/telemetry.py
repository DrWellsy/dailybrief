from __future__ import annotations

from dataclasses import dataclass
import re
import time

from rich.text import Text

from dailybrief.i18n import DEFAULT_LANG

# Pricing per 1,000,000 tokens (USD)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude": {"input": 3.00, "output": 15.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai": {"input": 2.50, "output": 10.00},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini": {"input": 0.15, "output": 0.60},
    "ollama": {"input": 0.0, "output": 0.0},
}

LOCKFILE_PATTERNS = [
    re.compile(r"(?i)diff --git a/.*?(?:package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|poetry\.lock|go\.sum)[\s\S]*?(?=(?:diff --git|$))"),
    re.compile(r"(?i)(?:package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|poetry\.lock|go\.sum)[\s\S]{500,}"),
]


@dataclass
class TelemetryData:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_seconds: float
    estimated_cost_usd: float
    redactions_count: int = 0
    loaded_from_cache: bool = False
    budget_truncated: bool = False


def estimate_tokens(text: str) -> int:
    """Estimates token count from text using empirical character ratio."""
    if not text:
        return 0
    return max(1, int(len(text) / 3.8))


def calculate_cost(provider_or_model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculates estimated cost in USD based on model pricing table."""
    key = (provider_or_model or "").lower().strip()

    rates = None
    for model_name, pricing in MODEL_PRICING.items():
        if model_name in key:
            rates = pricing
            break

    if rates is None:
        rates = MODEL_PRICING.get("claude", {"input": 3.00, "output": 15.00})

    input_cost = (input_tokens / 1_000_000.0) * rates["input"]
    output_cost = (output_tokens / 1_000_000.0) * rates["output"]
    return round(input_cost + output_cost, 5)


def enforce_context_budget(payload: str, max_chars: int = 40_000) -> tuple[str, bool]:
    """Ensures LLM context does not overflow by trimming lockfiles and oversized payloads."""
    if len(payload) <= max_chars:
        return payload, False

    processed = payload
    truncated = False

    # 1. Truncate noisy lockfile diffs first
    for pattern in LOCKFILE_PATTERNS:
        if pattern.search(processed):
            processed = pattern.sub("\n[... Lockfile diff truncated for context budget ...]\n", processed)
            truncated = True

    if len(processed) <= max_chars:
        return processed, truncated

    # 2. Hard clamp oversized remainder
    cutoff = max_chars - 100
    processed = processed[:cutoff] + "\n\n[... Remaining context truncated to fit token budget ...]"
    return processed, True


def render_telemetry_footer(telemetry: TelemetryData, lang: str = DEFAULT_LANG) -> Text:
    """Renders a sleek, subtle telemetry footer displaying tokens, latency, cost, and firewall status."""
    is_tr = (lang or DEFAULT_LANG).lower() == "tr"

    footer = Text()

    # Provider & Model
    p_info = telemetry.provider
    if telemetry.model and telemetry.model != telemetry.provider:
        p_info += f" ({telemetry.model})"
    footer.append(f"⚡ {p_info} ", style="bold cyan")
    footer.append("│ ", style="dim")

    # Tokens & Cache
    if telemetry.loaded_from_cache:
        token_str = "0 (Önbellek)" if is_tr else "0 (Cached)"
        footer.append(f"📊 {token_str} ", style="dim green")
    else:
        in_k = f"{telemetry.input_tokens / 1000.0:.1f}k" if telemetry.input_tokens >= 1000 else str(telemetry.input_tokens)
        out_k = f"{telemetry.output_tokens / 1000.0:.1f}k" if telemetry.output_tokens >= 1000 else str(telemetry.output_tokens)
        footer.append(f"📊 ~{in_k} in / {out_k} out ", style="dim")
    footer.append("│ ", style="dim")

    # Cost
    if telemetry.provider.lower() == "ollama":
        cost_str = "$0.0000 (Yerel)" if is_tr else "$0.0000 (Local)"
        footer.append(f"💰 {cost_str} ", style="green")
    elif telemetry.loaded_from_cache:
        footer.append("💰 $0.0000 ", style="green")
    else:
        footer.append(f"💰 Est: ${telemetry.estimated_cost_usd:.4f} ", style="dim")
    footer.append("│ ", style="dim")

    # Latency
    if telemetry.latency_seconds < 1.0:
        lat_str = f"{int(telemetry.latency_seconds * 1000)}ms"
    else:
        lat_str = f"{telemetry.latency_seconds:.1f}s"
    footer.append(f"⏱️ {lat_str} ", style="dim")
    footer.append("│ ", style="dim")

    # Firewall status
    if telemetry.redactions_count > 0:
        red_word = "Sansürlendi" if is_tr else "Redacted"
        footer.append(f"🛡️ {telemetry.redactions_count} {red_word}", style="bold yellow")
    else:
        clean_word = "Temiz" if is_tr else "Clean"
        footer.append(f"🛡️ Firewall: {clean_word}", style="dim green")

    # Budget cap indicator
    if telemetry.budget_truncated:
        cap_word = " ⚠️ Bütçe Kırpıldı" if is_tr else " ⚠️ Budget Capped"
        footer.append(cap_word, style="bold red")

    return footer
