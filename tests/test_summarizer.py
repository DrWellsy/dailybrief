from __future__ import annotations

import pytest

from dailybrief.git_context import GitContext
from dailybrief.i18n import get_message, get_system_prompt
from dailybrief.memory import HistoryEntry
from dailybrief.reader import Note
import dailybrief.summarizer as summarizer
from dailybrief.summarizer import generate_brief


class _FakeTextBlock:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.content = [_FakeTextBlock(text)]


class _FakeMessagesAPI:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.last_kwargs: dict = {}

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _FakeResponse(self._response_text)


class _FakeClient:
    def __init__(self, api_key: str, response_text: str = "Brief") -> None:
        self.api_key = api_key
        self.messages = _FakeMessagesAPI(response_text)


class _FakeAnthropicModule:
    class APIError(Exception):
        pass

    class APIConnectionError(APIError):
        pass

    class RateLimitError(APIError):
        pass

    def __init__(self, response_text: str = "Brief") -> None:
        self._response_text = response_text
        self.client = _FakeClient(api_key="", response_text=response_text)

    def Anthropic(self, api_key: str):
        self.client.api_key = api_key
        return self.client


def test_generate_brief_raises_when_api_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(summarizer, "_load_anthropic", lambda: _FakeAnthropicModule())

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        generate_brief([Note(name="n.md", content="content")], lang="en")

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        generate_brief([Note(name="n.md", content="content")], lang="tr")


def test_generate_brief_raises_when_empty_notes() -> None:
    with pytest.raises(RuntimeError, match="No notes provided"):
        generate_brief([], lang="en")

    with pytest.raises(RuntimeError, match="not bulunamadı"):
        generate_brief([], lang="tr")


def test_generate_brief_returns_text_en(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    fake_module = _FakeAnthropicModule(response_text="Daily Brief Text")
    monkeypatch.setattr(summarizer, "_load_anthropic", lambda: fake_module)

    result = generate_brief([Note(name="n.md", content="content")], lang="en")
    assert result == "Daily Brief Text"
    assert "strictly in English" in fake_module.client.messages.last_kwargs["system"]


def test_generate_brief_returns_text_tr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    fake_module = _FakeAnthropicModule(response_text="Türkçe Özet")
    monkeypatch.setattr(summarizer, "_load_anthropic", lambda: fake_module)

    result = generate_brief([Note(name="n.md", content="content")], lang="tr")
    assert result == "Türkçe Özet"
    assert "Türkçe" in fake_module.client.messages.last_kwargs["system"]


def test_generate_brief_with_git_and_history(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    fake_module = _FakeAnthropicModule(response_text="Integrated Brief")
    monkeypatch.setattr(summarizer, "_load_anthropic", lambda: fake_module)

    git_ctx = GitContext(
        branch="main",
        recent_commits=["abc1234 Initial commit"],
        uncommitted_count=1,
        modified_files=["cli.py"],
    )
    history = [
        HistoryEntry(
            date="2026-10-14",
            brief="Yesterday brief",
            lang="en",
            notes_count=2,
        )
    ]

    result = generate_brief(
        [Note(name="n.md", content="content")],
        lang="en",
        git_context=git_ctx,
        history=history,
    )
    assert result == "Integrated Brief"

    user_content = fake_module.client.messages.last_kwargs["messages"][0]["content"]
    assert "PREVIOUS BRIEFING MEMORY" in user_content
    assert "Yesterday brief" in user_content
    assert "GIT REPO CONTEXT" in user_content
    assert "Active Git Branch: main" in user_content


def test_generate_brief_rate_limit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")

    class _RateLimitedClient:
        class _Messages:
            def create(self, **kwargs):
                raise _FakeAnthropicModule.RateLimitError("rate limited")

        def __init__(self, api_key: str) -> None:
            self.messages = self._Messages()

    class _RateLimitAnthropicModule(_FakeAnthropicModule):
        def Anthropic(self, api_key: str):
            return _RateLimitedClient(api_key=api_key)

    monkeypatch.setattr(
        summarizer,
        "_load_anthropic",
        lambda: _RateLimitAnthropicModule(),
    )

    with pytest.raises(RuntimeError, match="rate limit"):
        generate_brief([Note(name="n.md", content="content")], lang="en")


def test_i18n_messages_and_prompts() -> None:
    assert "Daily Brief" in get_message("en", "panel_title")
    assert "Günlük Brifing" in get_message("tr", "panel_title")
    assert "Compiled from 3 file(s)" == get_message("en", "compiled_from", count=3)
    assert "3 dosyadan derlendi" == get_message("tr", "compiled_from", count=3)
    assert "English" in get_system_prompt("en")
    assert "Türkçe" in get_system_prompt("tr")
