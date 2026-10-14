from __future__ import annotations

from dailybrief.telemetry import (
    TelemetryData,
    calculate_cost,
    enforce_context_budget,
    estimate_tokens,
    render_telemetry_footer,
)


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    # ~38 characters -> ~10 tokens
    text = "The quick brown fox jumps over the lazy dog."
    assert 5 <= estimate_tokens(text) <= 20


def test_calculate_cost():
    # Claude Sonnet: $3.00/1M in, $15.00/1M out
    cost_claude = calculate_cost("claude-sonnet-4-6", input_tokens=1000, output_tokens=500)
    # (1000/1M)*3 + (500/1M)*15 = 0.003 + 0.0075 = 0.0105
    assert 0.010 <= cost_claude <= 0.011

    # Ollama is free
    cost_ollama = calculate_cost("ollama", input_tokens=5000, output_tokens=1000)
    assert cost_ollama == 0.0


def test_enforce_context_budget_under_limit():
    payload = "Short context under budget"
    res, truncated = enforce_context_budget(payload, max_chars=1000)
    assert not truncated
    assert res == payload


def test_enforce_context_budget_truncates_lockfile():
    lockfile_chunk = "package-lock.json\n" + ("  \"resolved\": \"https://registry.npmjs.org/dep/-/dep-1.0.0.tgz\"\n" * 50)
    payload = f"Notes:\nSome note\n\nDiff:\n{lockfile_chunk}"
    res, truncated = enforce_context_budget(payload, max_chars=len(payload) - 50)
    assert truncated
    assert "Lockfile diff truncated" in res


def test_enforce_context_budget_caps_massive_payload():
    payload = "A" * 5000
    res, truncated = enforce_context_budget(payload, max_chars=1000)
    assert truncated
    assert len(res) <= 1100
    assert "Remaining context truncated" in res


def test_render_telemetry_footer_live():
    telem = TelemetryData(
        provider="anthropic",
        model="claude-sonnet-4-6",
        input_tokens=1200,
        output_tokens=350,
        latency_seconds=1.5,
        estimated_cost_usd=0.0088,
        redactions_count=2,
        loaded_from_cache=False,
    )
    footer = render_telemetry_footer(telem, lang="en")
    plain = footer.plain
    assert "claude-sonnet-4-6" in plain
    assert "~1.2k in / 350 out" in plain
    assert "Est: $0.0088" in plain
    assert "1.5s" in plain
    assert "2 Redacted" in plain


def test_render_telemetry_footer_cached():
    telem = TelemetryData(
        provider="openai",
        model="gpt-4o",
        input_tokens=0,
        output_tokens=250,
        latency_seconds=0.018,
        estimated_cost_usd=0.0,
        redactions_count=0,
        loaded_from_cache=True,
    )
    footer = render_telemetry_footer(telem, lang="en")
    plain = footer.plain
    assert "0 (Cached)" in plain
    assert "$0.0000" in plain
    assert "18ms" in plain
    assert "Firewall: Clean" in plain


def test_render_telemetry_footer_ollama_local():
    telem = TelemetryData(
        provider="ollama",
        model="llama3.2",
        input_tokens=850,
        output_tokens=280,
        latency_seconds=2.1,
        estimated_cost_usd=0.0,
        redactions_count=0,
        loaded_from_cache=False,
    )
    footer_tr = render_telemetry_footer(telem, lang="tr")
    plain_tr = footer_tr.plain
    assert "ollama" in plain_tr
    assert "$0.0000 (Yerel)" in plain_tr
    assert "Firewall: Temiz" in plain_tr
