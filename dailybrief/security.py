from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Pattern

from rich.text import Text

from dailybrief.i18n import DEFAULT_LANG


@dataclass
class RedactionResult:
    text: str
    redacted_count: int
    details: dict[str, int] = field(default_factory=dict)

    @property
    def has_redactions(self) -> bool:
        return self.redacted_count > 0


# Pre-compiled high-performance secret detection regexes
SECRET_PATTERNS: list[tuple[str, Pattern[str], str]] = [
    # 1. Anthropic API Keys (sk-ant-api03-..., sk-ant-...)
    (
        "anthropic_key",
        re.compile(r"\bsk-ant-[a-zA-Z0-9_\-]{20,}\b"),
        "[REDACTED_API_KEY]",
    ),
    # 2. OpenAI API Keys (sk-..., sk-proj-...)
    (
        "openai_key",
        re.compile(r"\bsk-(?:proj-)?[a-zA-Z0-9_\-]{20,}\b"),
        "[REDACTED_API_KEY]",
    ),
    # 3. Google Gemini / Maps API Keys (AIza...)
    (
        "gemini_key",
        re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
        "[REDACTED_API_KEY]",
    ),
    # 4. GitHub Tokens (ghp_..., gho_..., ghu_..., ghs_..., ghr_..., github_pat_...)
    (
        "github_token",
        re.compile(r"\b(?:gh[pousr]_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{50,})\b"),
        "[REDACTED_TOKEN]",
    ),
    # 5. Slack Tokens (xoxb-..., xoxp-...)
    (
        "slack_token",
        re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b"),
        "[REDACTED_TOKEN]",
    ),
    # 6. AWS Access Key ID (AKIA...)
    (
        "aws_access_key",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "[REDACTED_AWS_KEY]",
    ),
    # 7. JWT Tokens (eyJ... . eyJ... . ...)
    (
        "jwt_token",
        re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
        "[REDACTED_JWT]",
    ),
    # 8. Private PEM / SSH Keys
    (
        "private_key",
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
        "[REDACTED_PRIVATE_KEY]",
    ),
    # 9. Bearer Authorization Headers / Tokens
    (
        "bearer_token",
        re.compile(r"(?i)\bBearer\s+[A-Za-z0-9\-._~+/]{20,}=*"),
        "Bearer [REDACTED_TOKEN]",
    ),
    # 10. Database Connection URLs with embedded credentials
    (
        "db_url",
        re.compile(r'''(?i)\b(?:postgres(?:ql)?|mongodb(?:\+srv)?|redis|mysql):\/\/[^\s:@/]+:[^\s@/]+@[^\s"'<>]+'''),
        "[REDACTED_DB_URL]",
    ),
    # 11. Generic assignments: password = "...", secret = "...", api_key = "..."
    (
        "generic_secret",
        re.compile(
            r'(?i)\b(password|passwd|secret|api_key|apikey|auth_token|access_token|client_secret)\s*[:=]\s*["\']([^"\'\s]{3,})["\']'
        ),
        r'\1 = "[REDACTED_SECRET]"',
    ),
]

PII_PATTERNS: list[tuple[str, Pattern[str], str]] = [
    # Email addresses
    (
        "email",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "[REDACTED_EMAIL]",
    ),
    # IPv4 addresses
    (
        "ipv4",
        re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"),
        "[REDACTED_IP]",
    ),
]


def redact_secrets(text: str, redact_pii: bool = False) -> RedactionResult:
    """Scans and redacts sensitive credentials, tokens, connection strings, and optional PII.

    Returns RedactionResult containing redacted text, total count of redactions, and breakdown.
    """
    if not text:
        return RedactionResult(text="", redacted_count=0, details={})

    processed = text
    total_count = 0
    details: dict[str, int] = {}

    # 1. Run core credential redactions
    for label, pattern, replacement in SECRET_PATTERNS:
        matches = list(pattern.finditer(processed))
        if matches:
            count = len(matches)
            total_count += count
            details[label] = details.get(label, 0) + count
            processed = pattern.sub(replacement, processed)

    # 2. Run optional PII redactions if requested
    if redact_pii:
        for label, pattern, replacement in PII_PATTERNS:
            matches = list(pattern.finditer(processed))
            if matches:
                count = len(matches)
                total_count += count
                details[label] = details.get(label, 0) + count
                processed = pattern.sub(replacement, processed)

    return RedactionResult(
        text=processed,
        redacted_count=total_count,
        details=details,
    )


def render_security_badge(redacted_count: int, lang: str = DEFAULT_LANG) -> Text | None:
    """Renders a reassuring terminal badge when sensitive tokens are intercepted."""
    if redacted_count <= 0:
        return None

    is_tr = (lang or DEFAULT_LANG).lower() == "tr"
    if is_tr:
        msg = f"🛡️  Güvenlik Duvarı: {redacted_count} hassas belirteç LLM'e iletilmeden önce sansürlendi"
    else:
        token_word = "token" if redacted_count == 1 else "tokens"
        msg = f"🛡️  Security Firewall: {redacted_count} sensitive {token_word} redacted before LLM transit"

    return Text(msg, style="bold green")
