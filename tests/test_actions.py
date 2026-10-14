from __future__ import annotations

from pathlib import Path

from dailybrief.actions import (
    append_task_breakdown,
    checkout_branch,
    copy_to_clipboard,
    export_brief,
    format_standup_text,
    generate_branch_name,
)


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


def test_generate_branch_name() -> None:
    bug_task = "1. Fix login session timeout bug before noon release"
    b_name = generate_branch_name(bug_task)
    assert b_name.startswith("fix/")
    assert "login" in b_name

    feat_task = "Finalize & publish v0.2.0 changelog to GitHub"
    f_name = generate_branch_name(feat_task)
    assert f_name.startswith("feat/")
    assert "finalize" in f_name or "publish" in f_name


def test_append_task_breakdown(tmp_path: Path) -> None:
    task_file = append_task_breakdown(
        breakdown_text="- Step 1: Reproduce\n- Step 2: Fix",
        task_title="Fix auth bug",
        date_str="2026-10-15",
        target_dir=tmp_path,
    )
    assert task_file.exists()
    assert task_file.name == "tasks-2026-10-15.md"
    content = task_file.read_text(encoding="utf-8")
    assert "## Task: Fix auth bug" in content
    assert "Step 1: Reproduce" in content

    # Append second task
    append_task_breakdown(
        breakdown_text="- Step 1: Design UI",
        task_title="Add Settings page",
        date_str="2026-10-15",
        target_dir=tmp_path,
    )
    updated = task_file.read_text(encoding="utf-8")
    assert "## Task: Fix auth bug" in updated
    assert "## Task: Add Settings page" in updated
