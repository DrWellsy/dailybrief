from __future__ import annotations

from pathlib import Path
import subprocess

from dailybrief.git_context import GitContext, collect_git_context


def test_git_context_format_for_prompt() -> None:
    ctx = GitContext(
        branch="feature/login",
        recent_commits=["abc1234 Add login flow", "def5678 Fix tests"],
        uncommitted_count=2,
        modified_files=["app.py", "auth.py"],
    )

    en_text = ctx.format_for_prompt(lang="en")
    assert "Active Git Branch: feature/login" in en_text
    assert "abc1234 Add login flow" in en_text
    assert "Uncommitted Working Changes: 2 file(s)" in en_text

    tr_text = ctx.format_for_prompt(lang="tr")
    assert "Aktif Git Dalı (Branch): feature/login" in tr_text
    assert "Son Git Commitleri" in tr_text


def test_collect_git_context_in_non_git_dir(tmp_path: Path) -> None:
    result = collect_git_context(repo_path=tmp_path)
    assert result is None


def test_collect_git_context_in_real_repo() -> None:
    # Current repo is a real git repo
    result = collect_git_context()
    assert result is not None
    assert isinstance(result.branch, str)
    assert isinstance(result.recent_commits, list)
    assert isinstance(result.uncommitted_count, int)
