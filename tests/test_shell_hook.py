from __future__ import annotations

import pytest

from dailybrief.shell_hook import generate_shell_hook


def test_generate_shell_hook_bash():
    snippet = generate_shell_hook("bash")
    assert "DailyBrief Auto-Greeting Hook (bash)" in snippet
    assert "_DB_TODAY=$(date +%Y-%m-%d)" in snippet
    assert "brief-$_DB_TODAY.md" in snippet
    assert "~/.bashrc" in snippet


def test_generate_shell_hook_zsh():
    snippet = generate_shell_hook("zsh")
    assert "DailyBrief Auto-Greeting Hook (zsh)" in snippet
    assert "~/.zshrc" in snippet


def test_generate_shell_hook_powershell():
    snippet = generate_shell_hook("powershell")
    assert "DailyBrief Auto-Greeting Hook (PowerShell)" in snippet
    assert "$PROFILE" in snippet
    assert "$dbToday = (Get-Date).ToString" in snippet
    assert "brief-$dbToday.md" in snippet


def test_generate_shell_hook_fish():
    snippet = generate_shell_hook("fish")
    assert "DailyBrief Auto-Greeting Hook (Fish)" in snippet
    assert "config.fish" in snippet
    assert "_db_brief" in snippet


def test_generate_shell_hook_unsupported():
    with pytest.raises(ValueError, match="Unsupported shell"):
        generate_shell_hook("tcsh")
