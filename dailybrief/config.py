from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import tomllib
from typing import Any

DEFAULT_CONFIG_DIR = Path.home() / ".dailybrief"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.toml"

DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4o",
    "gemini": "gemini-2.5-flash",
    "ollama": "llama3.2",
}

ENV_KEY_NAMES: dict[str, tuple[str, ...]] = {
    "anthropic": ("ANTHROPIC_API_KEY",),
    "openai": ("OPENAI_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "ollama": (),
}


@dataclass
class AppConfig:
    provider: str = "anthropic"
    model: str | None = None
    api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    elevenlabs_api_key: str | None = None
    ollama_host: str = "http://localhost:11434"
    voice_provider: str = "auto"
    voice_name: str = "alloy"
    watched_repos: list[str] = field(default_factory=list)


def load_config(config_path: Path | None = None) -> AppConfig:
    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        return AppConfig()

    try:
        raw_text = path.read_text(encoding="utf-8")
        data: dict[str, Any] = tomllib.loads(raw_text)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(f"Config could not be read: {path} ({exc})") from exc

    provider = str(data.get("provider", "anthropic")).lower().strip()
    model = data.get("model")
    if model is not None:
        model = str(model).strip()

    api_key = data.get("api_key")
    anthropic_api_key = data.get("anthropic_api_key") or api_key
    openai_api_key = data.get("openai_api_key")
    gemini_api_key = data.get("gemini_api_key")
    elevenlabs_api_key = data.get("elevenlabs_api_key")
    ollama_host = str(data.get("ollama_host", "http://localhost:11434")).strip()
    voice_provider = str(data.get("voice_provider", "auto")).strip().lower()
    voice_name = str(data.get("voice_name", "alloy")).strip()

    repos_raw = data.get("watched_repos", [])
    watched_repos = [str(r).strip() for r in repos_raw if str(r).strip()] if isinstance(repos_raw, list) else []

    return AppConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        anthropic_api_key=anthropic_api_key,
        openai_api_key=openai_api_key,
        gemini_api_key=gemini_api_key,
        elevenlabs_api_key=elevenlabs_api_key,
        ollama_host=ollama_host,
        voice_provider=voice_provider,
        voice_name=voice_name,
        watched_repos=watched_repos,
    )


def save_config(config: AppConfig, config_path: Path | None = None) -> Path:
    path = config_path or DEFAULT_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# DailyBrief Configuration",
        f"provider = {json.dumps(config.provider)}",
    ]
    if config.model:
        lines.append(f"model = {json.dumps(config.model)}")
    if config.api_key:
        lines.append(f"api_key = {json.dumps(config.api_key)}")
    if config.anthropic_api_key:
        lines.append(f"anthropic_api_key = {json.dumps(config.anthropic_api_key)}")
    if config.openai_api_key:
        lines.append(f"openai_api_key = {json.dumps(config.openai_api_key)}")
    if config.gemini_api_key:
        lines.append(f"gemini_api_key = {json.dumps(config.gemini_api_key)}")
    if config.elevenlabs_api_key:
        lines.append(f"elevenlabs_api_key = {json.dumps(config.elevenlabs_api_key)}")
    if config.ollama_host:
        lines.append(f"ollama_host = {json.dumps(config.ollama_host)}")
    if config.voice_provider:
        lines.append(f"voice_provider = {json.dumps(config.voice_provider)}")
    if config.voice_name:
        lines.append(f"voice_name = {json.dumps(config.voice_name)}")
    if config.watched_repos:
        repos_json = json.dumps(config.watched_repos)
        lines.append(f"watched_repos = {repos_json}")

    content = "\n".join(lines) + "\n"
    path.write_text(content, encoding="utf-8")
    return path


def resolve_api_key(provider: str, config: AppConfig) -> str | None:
    provider = provider.lower().strip()

    # Ollama requires no API key
    if provider == "ollama":
        return ""

    # Check environment variables
    env_keys = ENV_KEY_NAMES.get(provider, ())
    for env_var in env_keys:
        val = os.getenv(env_var)
        if val and val.strip():
            return val.strip()

    # Check config
    if provider == "anthropic":
        return config.anthropic_api_key or config.api_key
    elif provider == "openai":
        return config.openai_api_key
    elif provider == "gemini":
        return config.gemini_api_key

    return None


def set_api_key_for_provider(provider: str, api_key: str, config: AppConfig) -> None:
    provider = provider.lower().strip()
    if provider == "anthropic":
        config.anthropic_api_key = api_key
        config.api_key = api_key
    elif provider == "openai":
        config.openai_api_key = api_key
    elif provider == "gemini":
        config.gemini_api_key = api_key
