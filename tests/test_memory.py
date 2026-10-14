from __future__ import annotations

from pathlib import Path

from dailybrief.memory import (
    HistoryEntry,
    format_history_for_prompt,
    load_recent_history,
    save_history_entry,
)


def test_save_and_load_history(tmp_path: Path) -> None:
    save_history_entry(
        brief="Day 1 brief",
        date_str="2026-10-10",
        lang="en",
        notes_count=2,
        history_dir=tmp_path,
    )
    save_history_entry(
        brief="Day 2 brief",
        date_str="2026-10-11",
        lang="en",
        notes_count=3,
        history_dir=tmp_path,
    )

    entries = load_recent_history(days=5, history_dir=tmp_path)
    assert len(entries) == 2
    # Sorted descending by date
    assert entries[0].date == "2026-10-11"
    assert entries[0].brief == "Day 2 brief"
    assert entries[1].date == "2026-10-10"


def test_load_history_excludes_current_date(tmp_path: Path) -> None:
    save_history_entry(
        brief="Yesterday",
        date_str="2026-10-14",
        lang="en",
        notes_count=1,
        history_dir=tmp_path,
    )
    save_history_entry(
        brief="Today",
        date_str="2026-10-15",
        lang="en",
        notes_count=1,
        history_dir=tmp_path,
    )

    entries = load_recent_history(days=2, exclude_date="2026-10-15", history_dir=tmp_path)
    assert len(entries) == 1
    assert entries[0].date == "2026-10-14"


def test_format_history_for_prompt() -> None:
    entries = [
        HistoryEntry(
            date="2026-10-14",
            brief="1. Fix auth\n2. Release",
            lang="en",
            notes_count=2,
        )
    ]
    formatted = format_history_for_prompt(entries, lang="en")
    assert "Previous Briefing from 2026-10-14" in formatted
    assert "1. Fix auth" in formatted

    formatted_tr = format_history_for_prompt(entries, lang="tr")
    assert "Önceki Günün Brifingi (2026-10-14)" in formatted_tr
