from __future__ import annotations

import json
from pathlib import Path
import urllib.request

from dailybrief.voice import (
    clean_markdown_for_speech,
    generate_voice_script,
    play_audio_file,
    synthesize_brief_audio,
    synthesize_openai_speech,
)


class _MockTTSResponse:
    def __init__(self, raw_bytes: bytes) -> None:
        self._raw = raw_bytes

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_clean_markdown_for_speech() -> None:
    raw = "### Header\n- 1. **Fix** the `login` bug at [Link](http://example.com)!"
    cleaned = clean_markdown_for_speech(raw)
    assert "#" not in cleaned
    assert "**" not in cleaned
    assert "`" not in cleaned
    assert "Fix the login bug at Link!" in cleaned


def test_generate_voice_script_en() -> None:
    brief = """
Key Priorities for Today:
1. Fix login session timeout bug before noon release
2. Finalize v0.2.0 changelog

Things Not to Forget / Follow-ups:
• Standup status update at 10:30 AM
"""
    script = generate_voice_script(brief, "2026-10-15", lang="en")
    assert "Good morning" in script
    assert "2026-10-15" in script
    assert "Fix login session timeout bug" in script
    assert "Standup status update" in script


def test_generate_voice_script_tr() -> None:
    brief = """
Bugün Öncelikli 3-5 Madde:
- Login hatasını çöz
- Sürüm notlarını hazırla

Unutulmaması Gerekenler:
- Standup toplantısı
"""
    script = generate_voice_script(brief, "2026-10-15", lang="tr")
    assert "Günaydın" in script
    assert "2026-10-15" in script
    assert "Login hatasını çöz" in script
    assert "Standup toplantısı" in script


def test_synthesize_openai_speech(tmp_path: Path, monkeypatch) -> None:
    captured = {}

    def fake_urlopen(req, timeout=30):
        captured["url"] = req.full_url
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return _MockTTSResponse(b"FAKE_MP3_BYTES")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    target_file = tmp_path / "audio.mp3"
    success = synthesize_openai_speech("Test script", target_file, api_key="sk-test", voice="alloy")

    assert success is True
    assert target_file.exists()
    assert target_file.read_bytes() == b"FAKE_MP3_BYTES"
    assert captured["url"] == "https://api.openai.com/v1/audio/speech"
    assert captured["payload"]["voice"] == "alloy"


def test_synthesize_brief_audio_unavailable(tmp_path: Path, monkeypatch) -> None:
    # When no keys and no system speech
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("dailybrief.voice.synthesize_system_speech", lambda *args, **kwargs: False)

    path, provider = synthesize_brief_audio("Script", tmp_path / "out", provider="openai")
    assert path is None
    assert provider == "openai_failed"


def test_play_audio_file_non_existent(tmp_path: Path) -> None:
    assert play_audio_file(tmp_path / "missing.mp3") is False
