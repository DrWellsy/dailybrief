from __future__ import annotations

from pathlib import Path
import subprocess
import pytest

from dailybrief.scheduler import (
    get_dailybrief_executable_command,
    run_background_briefing,
    schedule_daily_task,
    send_desktop_notification,
    unschedule_daily_task,
    validate_time_str,
)


def test_validate_time_str_valid() -> None:
    assert validate_time_str("08:45") == (8, 45)
    assert validate_time_str("00:00") == (0, 0)
    assert validate_time_str("23:59") == (23, 59)
    assert validate_time_str("9:30") == (9, 30)


def test_validate_time_str_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid time format"):
        validate_time_str("invalid")

    with pytest.raises(ValueError, match="Invalid time range"):
        validate_time_str("24:00")

    with pytest.raises(ValueError, match="Invalid time range"):
        validate_time_str("12:65")


def test_get_dailybrief_executable_command() -> None:
    cmd = get_dailybrief_executable_command()
    assert "--background" in cmd


def test_schedule_daily_task_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.platform", "win32")

    executed_cmds: list[list[str]] = []

    def mock_run(cmd, **kwargs):
        executed_cmds.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="SUCCESS", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    ok, msg = schedule_daily_task("08:45", lang="en")
    assert ok is True
    assert "08:45" in msg
    assert len(executed_cmds) == 1
    assert executed_cmds[0][0] == "schtasks"
    assert "/st" in executed_cmds[0]
    assert "08:45" in executed_cmds[0]


def test_unschedule_daily_task_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.platform", "win32")

    executed_cmds: list[list[str]] = []

    def mock_run(cmd, **kwargs):
        executed_cmds.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="SUCCESS", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    ok, msg = unschedule_daily_task(lang="en")
    assert ok is True
    assert "removed successfully" in msg
    assert executed_cmds[0][:3] == ["schtasks", "/delete", "/tn"]


def test_send_desktop_notification_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.platform", "win32")

    executed = []

    def mock_run(cmd, **kwargs):
        executed.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr("subprocess.run", mock_run)

    success = send_desktop_notification("DailyBrief", "Test briefing ready")
    assert success is True
    assert len(executed) == 1
    assert executed[0][0] == "powershell"


def test_run_background_briefing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "note.md").write_text("- Task one\n- Task two", encoding="utf-8")

    from dailybrief.providers import LLMProvider

    class MockLLM(LLMProvider):
        @property
        def name(self) -> str:
            return "mock"
        @property
        def default_model(self) -> str:
            return "mock-model"
        def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
            return "Key Priorities for Today:\n1. Task one"

    monkeypatch.setattr("dailybrief.providers.get_provider", lambda *args, **kwargs: MockLLM())
    monkeypatch.setattr("dailybrief.scheduler.get_provider", lambda *args, **kwargs: MockLLM())
    monkeypatch.setattr("dailybrief.scheduler.resolve_api_key", lambda *args, **kwargs: "mock_key")

    notified = []
    monkeypatch.setattr("dailybrief.scheduler.send_desktop_notification", lambda title, msg: notified.append((title, msg)))

    res = run_background_briefing(source=notes_dir, lang="en")
    assert res is True
    assert len(notified) == 1
    assert "DailyBrief" in notified[0][0]
