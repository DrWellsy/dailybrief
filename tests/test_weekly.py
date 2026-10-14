from __future__ import annotations

from pathlib import Path

from dailybrief.memory import HistoryEntry, save_history_entry
from dailybrief.weekly import (
    WeeklyReport,
    format_weekly_standup,
    generate_weekly_report,
    render_weekly_panel,
)


def test_generate_weekly_report_with_history(tmp_path: Path):
    cfg_dir = tmp_path / ".dailybrief"
    cfg_dir.mkdir()

    # Save a couple history entries with priorities
    hist_dir = cfg_dir / "history"
    brief1 = (
        "Key Priorities for Today:\n"
        "- 1. Fix authentication cookie expiration bug\n"
        "- 2. Deploy redis caching layer\n"
        "\nThings Not to Forget:\n"
        "- Standup at 10am\n"
    )
    save_history_entry(brief1, date_str="2026-10-10", lang="en", notes_count=2, history_dir=hist_dir)

    brief2 = (
        "Key Priorities for Today:\n"
        "- 1. Fix authentication cookie expiration bug\n"
        "- 2. Refactor database migration scripts\n"
        "\nThings Not to Forget:\n"
        "- Review PR #42\n"
    )
    save_history_entry(brief2, date_str="2026-10-12", lang="en", notes_count=2, history_dir=hist_dir)

    report = generate_weekly_report(days=7, config_dir=cfg_dir, lang="en")
    assert isinstance(report, WeeklyReport)
    # Total unique planned tasks: auth cookie, redis caching, db migration
    total_tasks = len(report.completed_tasks) + len(report.carried_over_tasks)
    assert total_tasks >= 2
    assert 0.0 <= report.velocity_score <= 100.0


def test_render_weekly_panel():
    report = WeeklyReport(
        start_date="2026-10-08",
        end_date="2026-10-15",
        total_commits=14,
        completed_tasks=["Auth bug fix", "Redis deployment"],
        carried_over_tasks=["Refactor migration scripts"],
        velocity_score=66.7,
        summary_text="Weekly summary",
    )
    panel_en = render_weekly_panel(report, lang="en")
    assert "Weekly Retro" in panel_en.title
    assert "66.7%" in panel_en.title

    panel_tr = render_weekly_panel(report, lang="tr")
    assert "Weekly Retro" in panel_tr.title


def test_format_weekly_standup():
    report = WeeklyReport(
        start_date="2026-10-08",
        end_date="2026-10-15",
        total_commits=12,
        completed_tasks=["Deploy v0.2.0 release", "Add Ollama support"],
        carried_over_tasks=["Database sharding investigation"],
        velocity_score=66.7,
        summary_text="Weekly summary",
    )

    standup_en = format_weekly_standup(report, lang="en")
    assert "Weekly Engineering Retrospective" in standup_en
    assert "Velocity Score:" in standup_en
    assert "66.7%" in standup_en
    assert "- Deploy v0.2.0 release" in standup_en
    assert "- Database sharding investigation" in standup_en

    standup_tr = format_weekly_standup(report, lang="tr")
    assert "Haftalık Mühendislik Özeti" in standup_tr
    assert "Hız Skoru:" in standup_tr
    assert "%66.7" in standup_tr
