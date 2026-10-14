from __future__ import annotations

import io
import json
import urllib.error
import urllib.request

import pytest

from dailybrief.providers import (
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    OpenAIProvider,
    get_provider,
)


class _MockResponse:
    def __init__(self, data: dict, status: int = 200) -> None:
        self._raw = json.dumps(data).encode("utf-8")
        self.status = status

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_get_provider_factory() -> None:
    p_ant = get_provider("anthropic", api_key="test")
    assert isinstance(p_ant, AnthropicProvider)
    assert p_ant.name == "anthropic"

    p_oai = get_provider("openai", api_key="test")
    assert isinstance(p_oai, OpenAIProvider)
    assert p_oai.name == "openai"

    p_gem = get_provider("gemini", api_key="test")
    assert isinstance(p_gem, GeminiProvider)
    assert p_gem.name == "gemini"

    p_oll = get_provider("ollama", ollama_host="http://localhost:11434")
    assert isinstance(p_oll, OllamaProvider)
    assert p_oll.name == "ollama"

    with pytest.raises(ValueError, match="Unsupported provider"):
        get_provider("unknown_provider")


def test_openai_provider_generate(monkeypatch) -> None:
    captured_request = {}

    def fake_urlopen(req, timeout=30):
        captured_request["url"] = req.full_url
        captured_request["headers"] = dict(req.headers)
        captured_request["payload"] = json.loads(req.data.decode("utf-8"))
        return _MockResponse({"choices": [{"message": {"content": "OpenAI Brief"}}]})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    provider = OpenAIProvider(api_key="sk-test123")
    res = provider.generate("system prompt", "user prompt", model="gpt-4o")

    assert res == "OpenAI Brief"
    assert captured_request["url"] == "https://api.openai.com/v1/chat/completions"
    assert "Bearer sk-test123" in captured_request["headers"]["Authorization"]
    assert captured_request["payload"]["model"] == "gpt-4o"


def test_openai_provider_missing_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAIProvider(api_key=None)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not set"):
        provider.generate("sys", "user")


def test_gemini_provider_generate(monkeypatch) -> None:
    captured_request = {}

    def fake_urlopen(req, timeout=30):
        captured_request["url"] = req.full_url
        captured_request["payload"] = json.loads(req.data.decode("utf-8"))
        return _MockResponse({
            "candidates": [{
                "content": {"parts": [{"text": "Gemini Brief"}]}
            }]
        })

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    provider = GeminiProvider(api_key="gem-test123")
    res = provider.generate("sys prompt", "user prompt", model="gemini-2.5-flash")

    assert res == "Gemini Brief"
    assert "key=gem-test123" in captured_request["url"]
    assert captured_request["payload"]["systemInstruction"]["parts"][0]["text"] == "sys prompt"


def test_ollama_provider_generate(monkeypatch) -> None:
    captured_request = {}

    def fake_urlopen(req, timeout=60):
        captured_request["url"] = req.full_url
        captured_request["payload"] = json.loads(req.data.decode("utf-8"))
        return _MockResponse({"message": {"content": "Ollama Local Brief"}})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    provider = OllamaProvider(host="http://localhost:11434")
    res = provider.generate("sys", "user", model="llama3.2")

    assert res == "Ollama Local Brief"
    assert captured_request["url"] == "http://localhost:11434/api/chat"
    assert captured_request["payload"]["model"] == "llama3.2"


def test_ollama_provider_unreachable(monkeypatch) -> None:
    def fake_urlopen(req, timeout=60):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    provider = OllamaProvider(host="http://localhost:11434")
    with pytest.raises(RuntimeError, match="Ollama server is not reachable"):
        provider.generate("sys", "user")
