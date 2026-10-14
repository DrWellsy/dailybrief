from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from dailybrief.cli import main
from dailybrief.providers import LLMProvider


class MockProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "mock-model"

    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        return (
            "Key Priorities for Today:\n"
            "- 1. Ship v0.3.0 release\n"
            "- 2. Test DLP firewall\n"
            "\nThings Not to Forget:\n"
            "- Sync with team at 2pm\n"
        )


def test_cli_help_includes_phase4_flags():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "--redact-pii" in result.output
    assert "--no-todos" in result.output
    assert "--weekly" in result.output
    assert "--init-shell" in result.output


def test_cli_init_shell():
    runner = CliRunner()
    result_bash = runner.invoke(main, ["--init-shell", "bash"])
    assert result_bash.exit_code == 0
    assert "DailyBrief Auto-Greeting Hook (bash)" in result_bash.output

    result_pwsh = runner.invoke(main, ["--init-shell", "powershell"])
    assert result_pwsh.exit_code == 0
    assert "DailyBrief Auto-Greeting Hook (PowerShell)" in result_pwsh.output


def test_cli_weekly_mode(tmp_path: Path):
    runner = CliRunner()
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    result = runner.invoke(main, ["--weekly", "-s", str(notes_dir)], input="\n")
    assert result.exit_code == 0
    assert "Weekly Retro" in result.output
    assert "Velocity" in result.output


def test_cli_runs_with_security_badge_and_todos(tmp_path: Path):
    runner = CliRunner()
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()

    # Note contains secret that must be intercepted by DLP firewall
    note_file = notes_dir / "note.md"
    test_key = "sk-ant-" + "api03-abcdefghijklmnopqrstuvwxyz1234567890"
    note_file.write_text(
        f"Meeting with dev. Here is key {test_key} for testing.\n",
        encoding="utf-8",
    )

    with patch("dailybrief.cli._ensure_api_key", return_value="fake-key"), \
         patch("dailybrief.cli.get_provider", return_value=MockProvider()):
        result = runner.invoke(main, ["-s", str(notes_dir), "--force"])
        assert result.exit_code == 0
        assert "Daily Brief" in result.output
        assert "Security Firewall:" in result.output
        assert "sensitive" in result.output
        assert "mock-model" in result.output


def test_cli_no_todos_flag(tmp_path: Path):
    runner = CliRunner()
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "note.md").write_text("Regular note\n", encoding="utf-8")

    with patch("dailybrief.cli._ensure_api_key", return_value="fake-key"), \
         patch("dailybrief.cli.get_provider", return_value=MockProvider()), \
         patch("dailybrief.todo_scanner.scan_codebase_todos") as mock_scan:
        result = runner.invoke(main, ["-s", str(notes_dir), "--no-todos", "--force"])
        assert result.exit_code == 0
        # When --no-todos is given, scan_codebase_todos must not be called
        mock_scan.assert_not_called()
