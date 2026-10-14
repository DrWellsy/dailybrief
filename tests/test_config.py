from __future__ import annotations

import os
from pathlib import Path

from dailybrief.config import (
    AppConfig,
    load_config,
    resolve_api_key,
    save_config,
    set_api_key_for_provider,
)


def test_load_config_defaults(tmp_path: Path) -> None:
    non_existent = tmp_path / "non_existent.toml"
    config = load_config(non_existent)
    assert config.provider == "anthropic"
    assert config.ollama_host == "http://localhost:11434"
    assert config.watched_repos == []


def test_save_and_load_config(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.toml"
    original = AppConfig(
        provider="ollama",
        model="llama3.2:1b",
        api_key="legacy_key",
        anthropic_api_key="ant_key",
        openai_api_key="oai_key",
        gemini_api_key="gem_key",
        ollama_host="http://127.0.0.1:11434",
        watched_repos=["/repo1", "/repo2"],
    )
    save_config(original, cfg_file)

    loaded = load_config(cfg_file)
    assert loaded.provider == "ollama"
    assert loaded.model == "llama3.2:1b"
    assert loaded.anthropic_api_key == "ant_key"
    assert loaded.openai_api_key == "oai_key"
    assert loaded.gemini_api_key == "gem_key"
    assert loaded.ollama_host == "http://127.0.0.1:11434"
    assert loaded.watched_repos == ["/repo1", "/repo2"]


def test_resolve_api_key_from_env_and_config(monkeypatch) -> None:
    config = AppConfig(openai_api_key="cfg_openai")

    # Env takes precedence
    monkeypatch.setenv("OPENAI_API_KEY", "env_openai")
    assert resolve_api_key("openai", config) == "env_openai"

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert resolve_api_key("openai", config) == "cfg_openai"

    # Ollama needs no key
    assert resolve_api_key("ollama", config) == ""


def test_set_api_key_for_provider() -> None:
    cfg = AppConfig()
    set_api_key_for_provider("anthropic", "ant123", cfg)
    assert cfg.anthropic_api_key == "ant123"
    assert cfg.api_key == "ant123"

    set_api_key_for_provider("openai", "oai123", cfg)
    assert cfg.openai_api_key == "oai123"

    set_api_key_for_provider("gemini", "gem123", cfg)
    assert cfg.gemini_api_key == "gem123"
