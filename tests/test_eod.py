from __future__ import annotations

from pathlib import Path

from dailybrief.eod import (
    format_eod_standup,
    reconcile_eod,
    render_eod_panel,
    save_eod_summary,
)


def test_reconcile_eod_classifies_tasks() -> None:
    morning_brief = """
Key Priorities for Today:
1. Fix login session timeout bug before noon release
2. Add unit tests for payment webhook
3. Document onboarding flow for design team

Things Not to Forget:
- Team standup at 10:30
"""
    commits = ["Fix login session timeout bug in auth middleware"]
    modified = ["tests/test_webhook.py"]
    notes = ["- [ ] Working on items", "- [x] Did some other task"]

    eod = reconcile_eod(
        morning_brief=morning_brief,
        date_str="2026-10-15",
        git_commits=commits,
        git_modified_files=modified,
        note_contents=notes,
        lang="en",
    )

    assert eod.total_tasks == 3
    assert len(eod.completed) == 1
    assert "login session timeout" in eod.completed[0].title
    assert "Git commit:" in eod.completed[0].evidence

    assert len(eod.in_progress) == 1
    assert "unit tests for payment webhook" in eod.in_progress[0].title
    assert "Modified file:" in eod.in_progress[0].evidence

    assert len(eod.carried_over) == 1
    assert "Document onboarding flow" in eod.carried_over[0].title
    assert "Untouched today" in eod.carried_over[0].evidence

    assert abs(eod.completion_rate - 33.33) < 1.0


def test_reconcile_eod_checked_in_notes() -> None:
    morning_brief = """
Key Priorities for Today:
1. Deploy release candidate to staging
"""
    notes = ["# Sprint Log\n- [x] Deploy release candidate to staging"]
    eod = reconcile_eod(
        morning_brief=morning_brief,
        date_str="2026-10-15",
        note_contents=notes,
        lang="tr",
    )
    assert len(eod.completed) == 1
    assert eod.completed[0].status == "completed"
    assert "Notta tamamlandı:" in eod.completed[0].evidence


def test_render_eod_panel() -> None:
    morning_brief = "Key Priorities for Today:\n1. Fix bug"
    eod = reconcile_eod(morning_brief, "2026-10-15", git_commits=["Fix bug"])
    panel = render_eod_panel(eod, lang="en")
    assert "End-of-Day Wrap-Up" in str(panel.title)

    panel_tr = render_eod_panel(eod, lang="tr")
    assert "Gün Sonu Kapanışı" in str(panel_tr.title)


def test_format_eod_standup() -> None:
    morning_brief = "Key Priorities for Today:\n1. Task Done\n2. Task Pending"
    eod = reconcile_eod(morning_brief, "2026-10-15", git_commits=["Task Done"])
    standup_en = format_eod_standup(eod, lang="en")
    assert "End-of-Day Update" in standup_en
    assert "Task Done" in standup_en
    assert "Task Pending" in standup_en

    standup_tr = format_eod_standup(eod, lang="tr")
    assert "Gün Sonu Özeti" in standup_tr


def test_save_eod_summary(tmp_path: Path) -> None:
    morning_brief = "Key Priorities for Today:\n1. Task One"
    eod = reconcile_eod(morning_brief, "2026-10-15", git_commits=["Task One"])
    saved = save_eod_summary(eod, history_dir=tmp_path)
    assert saved.exists()
    assert saved.name == "2026-10-15-eod.json"
