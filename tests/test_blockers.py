from __future__ import annotations

from dailybrief.blockers import (
    BlockerAlert,
    are_tasks_similar,
    detect_blockers,
    extract_priorities_from_brief,
    render_blocker_panel,
)
from dailybrief.memory import HistoryEntry


def test_extract_priorities_from_brief_en() -> None:
    brief = """
Key Priorities for Today:
1. Fix login session timeout bug before noon release
2. Finalize & publish v0.2.0 changelog to GitHub
3. Align with design team on onboarding copy adjustments

Things Not to Forget / Follow-ups:
• Standup status update at 10:30 AM
"""
    tasks = extract_priorities_from_brief(brief)
    assert len(tasks) == 3
    assert tasks[0] == "Fix login session timeout bug before noon release"
    assert tasks[1] == "Finalize & publish v0.2.0 changelog to GitHub"
    assert tasks[2] == "Align with design team on onboarding copy adjustments"


def test_extract_priorities_from_brief_tr() -> None:
    brief = """
Bugün Öncelikli 3-5 Madde:
- Login timeout sorununu bugün çöz
- Analytics raporunu tamamla

Unutulmaması Gerekenler:
- Müşteri geri bildirimleri
"""
    tasks = extract_priorities_from_brief(brief)
    assert len(tasks) == 2
    assert tasks[0] == "Login timeout sorununu bugün çöz"
    assert tasks[1] == "Analytics raporunu tamamla"


def test_are_tasks_similar() -> None:
    t1 = "Fix login session timeout bug before noon"
    t2 = "Fix login timeout issue"
    assert are_tasks_similar(t1, t2) is True

    t3 = "Prepare deployment Docker container"
    assert are_tasks_similar(t1, t3) is False


def test_detect_blockers_finds_chronic_task() -> None:
    history = [
        HistoryEntry(
            date="2026-10-14",
            brief="Key Priorities for Today:\n1. Fix login timeout bug before noon\n2. Documentation\n\nThings Not to Forget:\n- Standup",
            lang="en",
            notes_count=2,
        ),
        HistoryEntry(
            date="2026-10-13",
            brief="Key Priorities for Today:\n1. Fix login session timeout bug\n2. Design review\n\nThings Not to Forget:\n- Call",
            lang="en",
            notes_count=2,
        ),
    ]

    # No git commits or modified files relating to login timeout
    commits = ["Update README.md", "Add sponsor link"]
    modified = ["README.md"]

    blockers = detect_blockers(history, git_commits=commits, git_modified_files=modified, lang="en")
    assert len(blockers) == 1
    assert "Fix login timeout" in blockers[0].task
    assert blockers[0].streak_days == 2
    assert "consecutive briefings" in blockers[0].advice


def test_detect_blockers_cleared_by_git_progress() -> None:
    history = [
        HistoryEntry(
            date="2026-10-14",
            brief="Key Priorities for Today:\n1. Fix login timeout bug before noon\n\nThings Not to Forget:\n- Standup",
            lang="en",
            notes_count=2,
        ),
        HistoryEntry(
            date="2026-10-13",
            brief="Key Priorities for Today:\n1. Fix login timeout bug\n\nThings Not to Forget:\n- Call",
            lang="en",
            notes_count=2,
        ),
    ]

    # Developer committed a fix for login!
    commits = ["Fix login timeout middleware issue"]
    modified = ["auth.py"]

    blockers = detect_blockers(history, git_commits=commits, git_modified_files=modified, lang="en")
    assert len(blockers) == 0


def test_render_blocker_panel() -> None:
    blockers = [
        BlockerAlert(task="Refactor auth token logic", streak_days=3, advice="Break down into subtasks")
    ]
    panel_en = render_blocker_panel(blockers, lang="en")
    assert panel_en is not None
    assert "Blocker / Carry-Over Alert" in str(panel_en.title)

    panel_tr = render_blocker_panel(blockers, lang="tr")
    assert panel_tr is not None
    assert "Tıkanıklık" in str(panel_tr.title)

    assert render_blocker_panel([]) is None
