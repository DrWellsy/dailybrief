from __future__ import annotations

from pathlib import Path

from dailybrief.actions import copy_to_clipboard, export_brief, format_standup_text


def test_format_standup_text() -> None:
    brief = "1. First task\n2. Second task"
    en_standup = format_standup_text(brief, "2026-10-15", lang="en")
    assert "Daily Standup (2026-10-15)" in en_standup
    assert "1. First task" in en_standup

    tr_standup = format_standup_text(brief, "2026-10-15", lang="tr")
    assert "Günlük Standup (2026-10-15)" in tr_standup


def test_export_brief(tmp_path: Path) -> None:
    out = export_brief("Sample content", "2026-10-15", output_dir=tmp_path)
    assert out.exists()
    assert out.name == "brief-2026-10-15.md"
    assert "Sample content" in out.read_text(encoding="utf-8")


def test_copy_to_clipboard() -> None:
    # Safe invocation; returns bool and does not crash
    result = copy_to_clipboard("test-copy")
    assert isinstance(result, bool)
