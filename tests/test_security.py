from __future__ import annotations

from dailybrief.security import redact_secrets, render_security_badge


def test_redact_anthropic_api_key():
    token = "sk-ant-" + "api03-abcdefghijklmnopqrstuvwxyz1234567890"
    raw = f"Here is my secret note: {token} for Claude."
    res = redact_secrets(raw)
    assert res.has_redactions
    assert "sk-ant-" not in res.text
    assert "[REDACTED_API_KEY]" in res.text
    assert res.details.get("anthropic_key") == 1


def test_redact_openai_api_key():
    k1 = "sk-proj-" + "1234567890abcdefghijklmnopqrstuvwxyz"
    k2 = "sk-" + "abcdefghijklmnopqrstuvwxyz123456"
    raw = f"OpenAI key is {k1} and older {k2}"
    res = redact_secrets(raw)
    assert res.redacted_count == 2
    assert "sk-proj-" not in res.text
    assert "[REDACTED_API_KEY]" in res.text


def test_redact_gemini_api_key():
    key = "AIza" + "SyA1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q"
    raw = f"Google Gemini key: {key}"
    res = redact_secrets(raw)
    assert res.has_redactions
    assert "AIza" not in res.text
    assert "[REDACTED_API_KEY]" in res.text


def test_redact_github_tokens():
    t1 = "ghp_" + "123456789012345678901234567890123456"
    t2 = "github_pat_" + "11AAAAAAA012345678901234567890123456789012345678901234567890123456"
    raw = f"Personal token: {t1}\nFine-grained token: {t2}"
    res = redact_secrets(raw)
    assert res.redacted_count == 2
    assert "ghp_" not in res.text
    assert "github_pat_" not in res.text
    assert "[REDACTED_TOKEN]" in res.text


def test_redact_slack_and_aws_keys():
    slack_tok = "xoxb" + "-123456789012-1234567890123-abcdefghijklmnopqrstuvwx"
    aws_tok = "AKIA" + "IOSFODNN7EXAMPLE"
    raw = f"Slack bot: {slack_tok}\nAWS: {aws_tok}"
    res = redact_secrets(raw)
    assert res.redacted_count == 2
    assert "xoxb-" not in res.text
    assert "AKIA" not in res.text
    assert "[REDACTED_TOKEN]" in res.text
    assert "[REDACTED_AWS_KEY]" in res.text


def test_redact_jwt_and_bearer_token():
    raw = (
        "Authorization: Bearer mySecretTokenString1234567890\n"
        "Session: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    res = redact_secrets(raw)
    assert res.has_redactions
    assert "Bearer [REDACTED_TOKEN]" in res.text
    assert "[REDACTED_JWT]" in res.text


def test_redact_database_url_with_credentials():
    raw = (
        "Database is postgres://db_user:s3cr3t_p@ssw0rd@db.internal.example.invalid:5432/production\n"
        "Mongo is mongodb+srv://mock_admin:SuperSecret99@mock-cluster.example.invalid/test"
    )
    res = redact_secrets(raw)
    assert res.redacted_count == 2
    assert "s3cr3t_p@ssw0rd" not in res.text
    assert "SuperSecret99" not in res.text
    assert "[REDACTED_DB_URL]" in res.text


def test_redact_private_pem_key_block():
    raw = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0Y1+7...test...key...data...\n"
        "-----END RSA PRIVATE KEY-----"
    )
    res = redact_secrets(raw)
    assert res.has_redactions
    assert "-----BEGIN RSA PRIVATE KEY-----" not in res.text
    assert "[REDACTED_PRIVATE_KEY]" in res.text


def test_redact_generic_assignments():
    raw = 'password = "SuperSecretPassword123!"\napi_key: "kjsdhf834928374982374928"'
    res = redact_secrets(raw)
    assert res.has_redactions
    assert "SuperSecretPassword123!" not in res.text
    assert "[REDACTED_SECRET]" in res.text


def test_redact_pii_flag():
    raw = "Contact Alice at alice@company.org or server 192.168.1.150 for issues."
    # With redact_pii=False, email and IP remain
    no_pii_res = redact_secrets(raw, redact_pii=False)
    assert no_pii_res.redacted_count == 0
    assert "alice@company.org" in no_pii_res.text

    # With redact_pii=True, email and IP are redacted
    pii_res = redact_secrets(raw, redact_pii=True)
    assert pii_res.redacted_count == 2
    assert "alice@company.org" not in pii_res.text
    assert "192.168.1.150" not in pii_res.text
    assert "[REDACTED_EMAIL]" in pii_res.text
    assert "[REDACTED_IP]" in pii_res.text


def test_render_security_badge():
    badge_en = render_security_badge(3, lang="en")
    assert badge_en is not None
    assert "3 sensitive tokens redacted" in badge_en.plain

    badge_tr = render_security_badge(1, lang="tr")
    assert badge_tr is not None
    assert "1 hassas belirteç" in badge_tr.plain

    assert render_security_badge(0) is None
