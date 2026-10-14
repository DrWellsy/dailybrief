from __future__ import annotations

from abc import ABC, abstractmethod
from importlib import import_module
import json
import os
import sys
from types import ModuleType
from typing import Any
import urllib.error
import urllib.request

from dailybrief.config import DEFAULT_MODELS


class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        ...

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        ...


def _load_anthropic() -> ModuleType:
    try:
        return import_module("anthropic")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Anthropic SDK kurulu degil / Anthropic SDK not installed. Run: pip install anthropic"
        ) from exc


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, load_anthropic_fn: Any = None) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._load_anthropic_fn = load_anthropic_fn

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODELS["anthropic"]

    def _get_anthropic_module(self) -> ModuleType:
        if self._load_anthropic_fn:
            return self._load_anthropic_fn()
        if "dailybrief.summarizer" in sys.modules:
            mod = sys.modules["dailybrief.summarizer"]
            if hasattr(mod, "_load_anthropic"):
                return mod._load_anthropic()
        return _load_anthropic()

    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        if not self.api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Please set the environment variable first:\n"
                "PowerShell: $env:ANTHROPIC_API_KEY='your_api_key'\n"
                "bash/zsh: export ANTHROPIC_API_KEY='your_api_key'"
            )

        active_model = model or self.default_model
        anthropic = self._get_anthropic_module()
        client = anthropic.Anthropic(api_key=self.api_key)

        try:
            response = client.messages.create(
                model=active_model,
                max_tokens=800,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
            )
        except getattr(anthropic, "RateLimitError", Exception) as exc:
            raise RuntimeError("Anthropic API rate limit reached. Please wait a moment and retry.") from exc
        except getattr(anthropic, "APIConnectionError", Exception) as exc:
            raise RuntimeError("Anthropic API connection error. Check your network connection.") from exc
        except getattr(anthropic, "APIError", Exception) as exc:
            raise RuntimeError(f"Anthropic API error: {exc}") from exc

        text_parts = [block.text for block in response.content if hasattr(block, "text")]
        brief = "\n".join(text_parts).strip()
        if not brief:
            raise RuntimeError("Anthropic API returned an empty response.")
        return brief


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    @property
    def name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODELS["openai"]

    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please set the environment variable or configure in ~/.dailybrief/config.toml:\n"
                "PowerShell: $env:OPENAI_API_KEY='your_api_key'\n"
                "bash/zsh: export OPENAI_API_KEY='your_api_key'"
            )

        active_model = model or self.default_model
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 800,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                choices = resp_data.get("choices", [])
                if choices:
                    return choices[0]["message"]["content"].strip()
                raise RuntimeError("OpenAI returned an empty response choices list.")
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 401:
                raise RuntimeError(f"OpenAI API authentication failed (401): {err_body}") from exc
            elif exc.code == 429:
                raise RuntimeError("OpenAI API rate limit exceeded (429). Please wait and retry.") from exc
            raise RuntimeError(f"OpenAI API HTTP error ({exc.code}): {err_body}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"OpenAI API connection error: {exc}") from exc


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODELS["gemini"]

    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY / GOOGLE_API_KEY is not set. Please set the environment variable:\n"
                "PowerShell: $env:GEMINI_API_KEY='your_api_key'\n"
                "bash/zsh: export GEMINI_API_KEY='your_api_key'"
            )

        active_model = model or self.default_model
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent"
            f"?key={self.api_key}"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"maxOutputTokens": 800},
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                candidates = resp_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        return text
                raise RuntimeError("Gemini returned an empty content candidate.")
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini API HTTP error ({exc.code}): {err_body}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"Gemini API connection error: {exc}") from exc


class OllamaProvider(LLMProvider):
    def __init__(self, host: str | None = None) -> None:
        self.host = (host or os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODELS["ollama"]

    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        active_model = model or self.default_model
        url = f"{self.host}/api/chat"
        payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                msg = resp_data.get("message", {}).get("content", "").strip()
                if not msg:
                    raise RuntimeError("Ollama returned an empty response.")
                return msg
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama HTTP error ({exc.code}): {err_body}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionRefusedError) as exc:
            raise RuntimeError(
                f"Ollama server is not reachable at {self.host}. "
                "Please make sure Ollama is installed and running ('ollama serve')."
            ) from exc


def get_provider(
    provider_name: str = "anthropic",
    api_key: str | None = None,
    ollama_host: str | None = None,
) -> LLMProvider:
    name = (provider_name or "anthropic").lower().strip()
    if name == "anthropic":
        return AnthropicProvider(api_key=api_key)
    elif name == "openai":
        return OpenAIProvider(api_key=api_key)
    elif name == "gemini":
        return GeminiProvider(api_key=api_key)
    elif name == "ollama":
        return OllamaProvider(host=ollama_host)
    else:
        raise ValueError(
            f"Unsupported provider: '{provider_name}'. Supported providers: anthropic, openai, gemini, ollama"
        )
