from __future__ import annotations

from pathlib import Path
import subprocess

from dailybrief.git_context import GitContext, GitRepoSummary, collect_git_context


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
    result = collect_git_context(repo_paths=[tmp_path])
    assert result is None


def test_collect_git_context_in_real_repo() -> None:
    # Current repo is a real git repo
    result = collect_git_context()
    assert result is not None
    assert isinstance(result.branch, str)
    assert isinstance(result.recent_commits, list)
    assert isinstance(result.uncommitted_count, int)


def test_multi_repo_git_context_format() -> None:
    r1 = GitRepoSummary(
        path=Path("/workspace/dailybrief"),
        name="dailybrief",
        branch="main",
        recent_commits=["abc1234 Fix timeout"],
        uncommitted_count=1,
        modified_files=["cli.py"],
    )
    r2 = GitRepoSummary(
        path=Path("/workspace/api-backend"),
        name="api-backend",
        branch="feat/auth",
        recent_commits=["def5678 Add JWT verification"],
        uncommitted_count=0,
        modified_files=[],
    )

    multi_ctx = GitContext(
        branch="main",
        recent_commits=["[dailybrief] abc1234 Fix timeout", "[api-backend] def5678 Add JWT verification"],
        uncommitted_count=1,
        modified_files=["[dailybrief] cli.py"],
        repos=[r1, r2],
    )

    en_prompt = multi_ctx.format_for_prompt(lang="en")
    assert "Active Git Repositories (2):" in en_prompt
    assert "• Depo / Repo 'dailybrief' (Branch: main):" in en_prompt
    assert "• Depo / Repo 'api-backend' (Branch: feat/auth):" in en_prompt
    assert "Fix timeout" in en_prompt
    assert "Add JWT verification" in en_prompt

    banner_en = multi_ctx.format_banner(lang="en")
    assert "Watching 2 repo(s)" in banner_en
    assert "dailybrief ('main')" in banner_en

    banner_tr = multi_ctx.format_banner(lang="tr")
    assert "2 Git deposu izleniyor" in banner_tr
