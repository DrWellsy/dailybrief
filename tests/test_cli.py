from __future__ import annotations

from pathlib import Path
from click.testing import CliRunner
import pytest

from dailybrief.cli import main
from dailybrief.memory import HistoryEntry, save_history_entry
from dailybrief.providers import LLMProvider


class _MockLLMProvider(LLMProvider):
    def __init__(self, response_text: str = "Key Priorities for Today:\n1. Test CLI feature\n\nThings Not to Forget:\n- Standup") -> None:
        self.response_text = response_text
        self.last_system_prompt = ""
        self.last_user_prompt = ""

    @property
    def name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "mock-model"

    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response_text


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "--provider" in result.output
    assert "--git-repo" in result.output
    assert "--interactive" in result.output


def test_cli_no_notes(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--source", str(tmp_path)])
    assert result.exit_code == 0
    assert "0 file(s)" in result.output or "0 dosya" in result.output


def test_cli_runs_with_mock_provider(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Create a note
    (tmp_path / "task.md").write_text("- Fix login timeout", encoding="utf-8")

    mock_provider = _MockLLMProvider("Key Priorities for Today:\n1. Fix login bug\n\nThings Not to Forget:\n- Standup")
    monkeypatch.setattr("dailybrief.cli.get_provider", lambda *args, **kwargs: mock_provider)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--source", str(tmp_path), "--provider", "ollama", "--no-git", "--no-history"],
    )

    assert result.exit_code == 0
    assert "DailyBrief" in result.output
    assert "Fix login bug" in result.output


def test_cli_displays_blocker_alert(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "todo.md").write_text("- Working on tasks", encoding="utf-8")

    history_dir = tmp_path / "history"
    save_history_entry(
        brief="Key Priorities for Today:\n1. Unresolved database lock issue\n\nThings Not to Forget:\n- Meeting",
        date_str="2026-10-14",
        lang="en",
        notes_count=1,
        history_dir=history_dir,
    )
    save_history_entry(
        brief="Key Priorities for Today:\n1. Unresolved database lock issue\n\nThings Not to Forget:\n- Meeting",
        date_str="2026-10-13",
        lang="en",
        notes_count=1,
        history_dir=history_dir,
    )

    monkeypatch.setattr("dailybrief.cli.load_recent_history", lambda *args, **kwargs: [
        HistoryEntry("2026-10-14", "Key Priorities for Today:\n1. Unresolved database lock issue\n\nThings Not to Forget:\n- Meeting", "en", 1),
        HistoryEntry("2026-10-13", "Key Priorities for Today:\n1. Unresolved database lock issue\n\nThings Not to Forget:\n- Meeting", "en", 1),
    ])

    mock_provider = _MockLLMProvider("Key Priorities for Today:\n1. Today task\n\nThings Not to Forget:\n- Standup")
    monkeypatch.setattr("dailybrief.cli.get_provider", lambda *args, **kwargs: mock_provider)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--source", str(notes_dir), "--provider", "ollama", "--no-git"],
    )

    assert result.exit_code == 0
    assert "Blocker / Carry-Over Alert" in result.output
    assert "Unresolved database lock" in result.output


def test_cli_interactive_menu_exit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "task.md").write_text("- Test task", encoding="utf-8")
    mock_provider = _MockLLMProvider("Key Priorities for Today:\n1. Sample task\n\nThings Not to Forget:\n- Note")
    monkeypatch.setattr("dailybrief.cli.get_provider", lambda *args, **kwargs: mock_provider)

    # Input 'q' to quit interactive loop
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--source", str(tmp_path), "--provider", "ollama", "--interactive", "--no-git", "--no-history"],
        input="q\n",
    )

    assert result.exit_code == 0
    assert "Daily Brief" in result.output


def test_cli_help_includes_v2_flags() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "--eod" in result.output
    assert "--voice" in result.output
    assert "--mcp" in result.output


def test_cli_mcp_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    called = []
    monkeypatch.setattr("dailybrief.cli.run_mcp_server", lambda: called.append(True))

    runner = CliRunner()
    result = runner.invoke(main, ["--mcp"])
    assert result.exit_code == 0
    assert called == [True]


def test_cli_eod_no_morning_brief(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("dailybrief.cli.load_recent_history", lambda *args, **kwargs: [])

    runner = CliRunner()
    result = runner.invoke(main, ["--eod", "--no-git"])
    assert result.exit_code == 0
    assert "DailyBrief End-of-Day" in result.output or "Sabah brifingi bulunamadı" in result.output or "No morning briefing" in result.output


def test_cli_eod_with_morning_brief(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "tasks.md").write_text("- [x] Resolve database lock issue", encoding="utf-8")

    brief_text = "Key Priorities for Today:\n1. Resolve database lock issue\n2. Ship API endpoint"
    entry = HistoryEntry(
        date="2026-10-14",
        brief=brief_text,
        lang="en",
        notes_count=1,
    )
    monkeypatch.setattr("dailybrief.cli.load_recent_history", lambda *args, **kwargs: [entry])

    # Avoid interactive prompt
    runner = CliRunner()
    result = runner.invoke(main, ["--source", str(notes_dir), "--eod", "--no-git"])
    assert result.exit_code == 0
    assert "End-of-Day" in result.output or "Gun Sonu" in result.output
    assert "Resolve database lock" in result.output


def test_cli_voice_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "tasks.md").write_text("- Write tests", encoding="utf-8")
    mock_provider = _MockLLMProvider("Key Priorities for Today:\n1. Write tests\n\nThings Not to Forget:\n- Drink coffee")
    monkeypatch.setattr("dailybrief.cli.get_provider", lambda *args, **kwargs: mock_provider)

    synth_called = []
    play_called = []

    def mock_synth(text: str, **kwargs):
        synth_called.append(text)
        dummy_file = tmp_path / "dummy.wav"
        dummy_file.write_bytes(b"RIFFdummyWAVE")
        return dummy_file, "mock_tts"

    def mock_play(path: Path, **kwargs):
        play_called.append(path)
        return True

    monkeypatch.setattr("dailybrief.cli.synthesize_brief_audio", mock_synth)
    monkeypatch.setattr("dailybrief.cli.play_audio_file", mock_play)

    runner = CliRunner()
    result = runner.invoke(main, ["--source", str(tmp_path), "--provider", "ollama", "--voice", "--no-git", "--no-history"])

    assert result.exit_code == 0
    assert len(synth_called) == 1
    assert len(play_called) == 1


def test_cli_git_radar_display(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "notes.md").write_text("- Refactor auth.py", encoding="utf-8")
    mock_provider = _MockLLMProvider("Key Priorities for Today:\n1. Refactor auth\n\nThings Not to Forget:\n- Standup")
    monkeypatch.setattr("dailybrief.cli.get_provider", lambda *args, **kwargs: mock_provider)

    from dailybrief.git_radar import GitRadarAlert
    fake_alert = GitRadarAlert(
        repo_name="myrepo",
        upstream_branch="origin/main",
        behind_count=2,
        ahead_count=0,
        conflicting_files=["auth.py"],
        upstream_commits=["feat: update auth middleware"],
        advice="Pull or rebase upstream/main before coding to prevent merge conflicts.",
    )
    monkeypatch.setattr("dailybrief.cli.inspect_git_radar", lambda *args, **kwargs: [fake_alert])

    runner = CliRunner()
    result = runner.invoke(main, ["--source", str(tmp_path), "--provider", "ollama", "--no-history"])

    assert result.exit_code == 0
    assert "Git Radar" in result.output or "Git Radarı" in result.output
    assert "auth.py" in result.output


def test_cli_doctor(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--doctor", "--source", str(tmp_path)])
    assert result.exit_code == 0
    assert "Doctor" in result.output or "Tanılama" in result.output
    assert "Config" in result.output


def test_cli_schedule_and_unschedule(monkeypatch: pytest.MonkeyPatch) -> None:
    sched_calls = []
    unsched_calls = []
    monkeypatch.setattr("dailybrief.scheduler.schedule_daily_task", lambda t, lang: sched_calls.append(t) or (True, "Scheduled"))
    monkeypatch.setattr("dailybrief.scheduler.unschedule_daily_task", lambda lang: unsched_calls.append(True) or (True, "Unscheduled"))

    runner = CliRunner()
    res1 = runner.invoke(main, ["--schedule", "08:45"])
    assert res1.exit_code == 0
    assert sched_calls == ["08:45"]
    assert "Scheduled" in res1.output

    res2 = runner.invoke(main, ["--unschedule"])
    assert res2.exit_code == 0
    assert unsched_calls == [True]
    assert "Unscheduled" in res2.output


def test_cli_background(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bg_calls = []
    monkeypatch.setattr("dailybrief.scheduler.run_background_briefing", lambda **kwargs: bg_calls.append(kwargs) or True)

    runner = CliRunner()
    res = runner.invoke(main, ["--background", "--source", str(tmp_path)])
    assert res.exit_code == 0
    assert len(bg_calls) == 1


def test_cli_cache_and_force(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "task.md").write_text("- Caching test note", encoding="utf-8")
    call_count = [0]

    class CountingMockProvider(_MockLLMProvider):
        def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
            call_count[0] += 1
            return f"Key Priorities for Today:\n1. Run {call_count[0]}\n\nThings Not to Forget:\n- Standup"

    provider = CountingMockProvider()
    monkeypatch.setattr("dailybrief.cli.get_provider", lambda *args, **kwargs: provider)

    # Use a unique isolated cache dir for this test
    custom_cache = tmp_path / "custom_cache"
    monkeypatch.setattr("dailybrief.cache.CACHE_DIR", custom_cache)

    runner = CliRunner()

    # 1. First run: cold cache -> calls LLM
    res1 = runner.invoke(main, ["--source", str(tmp_path), "--provider", "ollama", "--no-git", "--no-history"])
    assert res1.exit_code == 0
    assert call_count[0] == 1
    assert "Run 1" in res1.output
    assert "0 tokens used" not in res1.output

    # 2. Second run: hit cache -> does NOT call LLM, shows badge
    res2 = runner.invoke(main, ["--source", str(tmp_path), "--provider", "ollama", "--no-git", "--no-history"])
    assert res2.exit_code == 0
    assert call_count[0] == 1  # unchanged!
    assert "Run 1" in res2.output
    assert "0 tokens used" in res2.output

    # 3. Third run: with --force -> bypasses cache, calls LLM
    res3 = runner.invoke(main, ["--source", str(tmp_path), "--provider", "ollama", "--no-git", "--no-history", "--force"])
    assert res3.exit_code == 0
    assert call_count[0] == 2  # incremented!
    assert "Run 2" in res3.output


