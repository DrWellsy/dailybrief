from __future__ import annotations

from pathlib import Path
import subprocess

from dailybrief.git_radar import (
    GitRadarAlert,
    inspect_git_radar,
    inspect_single_repo_radar,
    render_radar_panel,
)


def test_inspect_git_radar_non_git_dir(tmp_path: Path) -> None:
    alerts = inspect_git_radar(repo_paths=[tmp_path])
    assert alerts == []


def test_render_radar_panel() -> None:
    alert = GitRadarAlert(
        repo_name="dailybrief",
        upstream_branch="origin/main",
        behind_count=3,
        ahead_count=1,
        conflicting_files=["dailybrief/cli.py"],
        upstream_commits=["abc1234 Update CLI flags", "def5678 Fix parser"],
        advice="Pull or rebase recommended before editing conflicting files.",
    )

    panel_en = render_radar_panel([alert], lang="en")
    assert panel_en is not None
    assert "Git Radar / Upstream Conflict Warning" in str(panel_en.title)

    panel_tr = render_radar_panel([alert], lang="tr")
    assert panel_tr is not None
    assert "Git Radarı / Çakışma Riski" in str(panel_tr.title)

    assert render_radar_panel([]) is None


def test_inspect_single_repo_radar_mocked(tmp_path: Path, monkeypatch) -> None:
    # Mock subprocess.run to simulate upstream divergence
    def fake_run(cmd, cwd=None, capture_output=True, text=True, check=False, timeout=None):
        cmd_str = " ".join(cmd)
        if "--is-inside-work-tree" in cmd_str:
            return subprocess.CompletedProcess(cmd, 0, stdout="true", stderr="")
        elif "@{u}" in cmd_str:
            return subprocess.CompletedProcess(cmd, 0, stdout="origin/main", stderr="")
        elif "HEAD...origin/main" in cmd_str:
            # 1 ahead, 2 behind
            return subprocess.CompletedProcess(cmd, 0, stdout="1 2", stderr="")
        elif "--name-only" in cmd_str:
            return subprocess.CompletedProcess(cmd, 0, stdout="auth.py\ncli.py\n", stderr="")
        elif "--oneline" in cmd_str:
            return subprocess.CompletedProcess(cmd, 0, stdout="a1b2c3d Upstream commit\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    alert = inspect_single_repo_radar(
        repo_path=tmp_path,
        local_modified_files=["auth.py"],
        lang="en",
    )

    assert alert is not None
    assert alert.behind_count == 2
    assert alert.ahead_count == 1
    assert "auth.py" in alert.conflicting_files
    assert len(alert.upstream_commits) == 1
    assert "git pull --rebase" in alert.advice
