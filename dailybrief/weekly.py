from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
import re
import shutil
import subprocess

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dailybrief.blockers import are_tasks_similar, detect_blockers, extract_priorities_from_brief
from dailybrief.config import DEFAULT_CONFIG_DIR
from dailybrief.i18n import DEFAULT_LANG
from dailybrief.memory import HistoryEntry, load_recent_history


@dataclass
class WeeklyReport:
    start_date: str
    end_date: str
    total_commits: int
    commits: list[str] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    carried_over_tasks: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    velocity_score: float = 100.0
    summary_text: str = ""


def collect_weekly_commits(
    repos: list[Path | str] | None = None,
    days: int = 7,
) -> list[str]:
    """Collects git commit messages from the last `days` across watched repositories."""
    if not shutil.which("git"):
        return []

    target_repos: list[Path] = []
    if repos:
        for r in repos:
            p = Path(r)
            if p.is_dir():
                target_repos.append(p)
    else:
        target_repos.append(Path.cwd())

    all_commits: list[str] = []
    since_arg = f"--since={days} days ago"

    for repo_path in target_repos:
        try:
            proc = subprocess.run(
                ["git", "log", since_arg, "--oneline"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if proc.returncode == 0 and proc.stdout:
                for line in proc.stdout.splitlines():
                    cleaned = line.strip()
                    if cleaned:
                        all_commits.append(cleaned)
        except Exception:
            continue

    return all_commits


def _find_checked_tasks_in_dir(search_dir: Path) -> set[str]:
    checked_tasks: set[str] = set()
    if not search_dir.exists():
        return checked_tasks

    for fpath in search_dir.glob("*.md"):
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                m = re.match(r"^\s*[-*]\s*\[[xX]\]\s*(.+)$", line)
                if m:
                    checked_tasks.add(m.group(1).strip().lower())
        except Exception:
            continue

    return checked_tasks


def generate_weekly_report(
    days: int = 7,
    repos: list[Path | str] | None = None,
    source_dir: Path | str | None = None,
    config_dir: Path | str | None = None,
    lang: str = DEFAULT_LANG,
) -> WeeklyReport:
    """Synthesizes the past week of daily briefings, git commits, and completed tasks."""
    today = date.today()
    start_dt = today - timedelta(days=days)
    end_date_str = today.strftime("%Y-%m-%d")
    start_date_str = start_dt.strftime("%Y-%m-%d")

    # 1. Load history entries
    hist_dir = Path(config_dir) / "history" if config_dir else None
    history_entries = load_recent_history(days=days, history_dir=hist_dir)

    # 2. Collect git commits
    commits = collect_weekly_commits(repos=repos, days=days)

    # 3. Collect explicitly completed [x] tasks from notes and history dir
    checked_tasks = set()
    cfg_path = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR
    checked_tasks.update(_find_checked_tasks_in_dir(cfg_path))
    if source_dir:
        checked_tasks.update(_find_checked_tasks_in_dir(Path(source_dir)))

    # 4. Extract all planned priorities across the week
    all_planned: list[str] = []
    task_occurrence: dict[str, int] = {}

    for entry in history_entries:
        priorities = extract_priorities_from_brief(entry.brief)
        for p in priorities:
            normalized = p.strip()
            all_planned.append(normalized)
            # Find matching existing key or add new
            matched_key = None
            for existing in task_occurrence:
                if are_tasks_similar(existing, normalized):
                    matched_key = existing
                    break
            if matched_key:
                task_occurrence[matched_key] += 1
            else:
                task_occurrence[normalized] = 1

    # 5. Classify tasks into completed vs carried-over
    completed: list[str] = []
    carried_over: list[str] = []

    for task_name, count in task_occurrence.items():
        # Check if completed via git commit
        is_git_done = any(are_tasks_similar(task_name, commit) for commit in commits)
        # Check if marked [x]
        is_checked_done = any(are_tasks_similar(task_name, chk) for chk in checked_tasks)

        if is_git_done or is_checked_done or count == 1:
            completed.append(task_name)
        else:
            carried_over.append(task_name)

    # If carried over tasks exist, check chronic blockers
    detected_blockers = detect_blockers(
        history_entries=history_entries,
        git_commits=commits,
        lang=lang,
    )
    blocker_descriptions = [b.task for b in detected_blockers]

    total_unique = len(completed) + len(carried_over)
    velocity = (len(completed) / total_unique * 100.0) if total_unique > 0 else 100.0
    velocity = round(velocity, 1)

    is_tr = (lang or DEFAULT_LANG).lower() == "tr"
    if is_tr:
        summary_lines = [
            f"# Haftalık Sprint Retrospektifi ({start_date_str} - {end_date_str})",
            f"- Hız Skoru: %{velocity} ({len(completed)}/{total_unique} görev tamamlandı)",
            f"- Toplam Git Commit'i: {len(commits)}",
            f"- Devam Eden / Tıkanan Görevler: {len(carried_over)}",
        ]
    else:
        summary_lines = [
            f"# Weekly Sprint Retrospective ({start_date_str} - {end_date_str})",
            f"- Velocity Score: {velocity}% ({len(completed)}/{total_unique} tasks completed)",
            f"- Total Git Commits: {len(commits)}",
            f"- Carried-Over / Blocked Tasks: {len(carried_over)}",
        ]

    return WeeklyReport(
        start_date=start_date_str,
        end_date=end_date_str,
        total_commits=len(commits),
        commits=commits,
        completed_tasks=completed,
        carried_over_tasks=carried_over,
        blockers=blocker_descriptions,
        velocity_score=velocity,
        summary_text="\n".join(summary_lines),
    )


def render_weekly_panel(report: WeeklyReport, lang: str = DEFAULT_LANG) -> Panel:
    """Renders a comprehensive Rich panel with Developer Velocity Scorecard & Retrospective."""
    is_tr = (lang or DEFAULT_LANG).lower() == "tr"

    title = (
        f"📈 Haftalık Sprint Retrospektifi ({report.start_date} - {report.end_date})"
        if is_tr
        else f"📈 Weekly Sprint Retrospective ({report.start_date} - {report.end_date})"
    )

    table = Table.grid(padding=(0, 2))
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="bold")

    # Velocity row with color coding
    vel_style = "bold green" if report.velocity_score >= 80 else ("bold yellow" if report.velocity_score >= 50 else "bold red")
    total_tasks = len(report.completed_tasks) + len(report.carried_over_tasks)
    vel_label = "🎯 Hız Skoru / Velocity:" if is_tr else "🎯 Velocity Score:"
    table.add_row(vel_label, Text(f"{report.velocity_score}% ({len(report.completed_tasks)}/{total_tasks} tasks)", style=vel_style))

    # Commits row
    com_label = "🐙 Git Commitleri:" if is_tr else "🐙 Git Activity:"
    table.add_row(com_label, Text(f"{report.total_commits} commits across watched repos", style="dim"))

    # Blockers row
    blocker_count = len(report.blockers)
    blk_style = "bold green" if blocker_count == 0 else "bold red"
    blk_label = "⚡ Kronik Tıkanıklık:" if is_tr else "⚡ Chronic Blockers:"
    blk_val = f"{blocker_count} detected" if blocker_count > 0 else ("0 (Temiz)" if is_tr else "0 (Clean)")
    table.add_row(blk_label, Text(blk_val, style=blk_style))

    content = Text()
    content.append(f"{title}\n\n", style="bold cyan")

    # Add highlights
    comp_header = "✅ Bu Hafta Tamamlananlar / Completed Highlights:" if is_tr else "✅ Completed Highlights This Week:"
    content.append(f"{comp_header}\n", style="bold green")
    if report.completed_tasks:
        for t in report.completed_tasks[:5]:
            content.append(f"  • {t}\n", style="dim")
        if len(report.completed_tasks) > 5:
            more_cnt = len(report.completed_tasks) - 5
            content.append(f"  ... +{more_cnt} more\n", style="dim")
    else:
        none_msg = "  (Kayıtlı tamamlanan görev yok)\n" if is_tr else "  (No completed tasks recorded)\n"
        content.append(none_msg, style="dim")

    content.append("\n")

    # Add carried over / blockers
    if report.carried_over_tasks:
        carry_header = "⚠️ Gelecek Haftaya Devredenler / Carried Over:" if is_tr else "⚠️ Carried Over to Next Sprint:"
        content.append(f"{carry_header}\n", style="bold yellow")
        for t in report.carried_over_tasks[:4]:
            content.append(f"  • {t}\n", style="dim yellow")
        content.append("\n")

    return Panel(
        content,
        title=f"Weekly Retro ({report.velocity_score}% Velocity)",
        border_style="cyan",
        padding=(1, 2),
    )


def format_weekly_standup(report: WeeklyReport, lang: str = DEFAULT_LANG) -> str:
    """Formats a weekly retro standup update for Slack, Teams, or Friday sync."""
    is_tr = (lang or DEFAULT_LANG).lower() == "tr"

    if is_tr:
        lines = [
            f"📊 *Haftalık Mühendislik Özeti ({report.start_date} - {report.end_date})*",
            f"🎯 *Hız Skoru:* %{report.velocity_score}",
            f"🐙 *Git Commit Sayısı:* {report.total_commits}",
            "",
            "*✅ Tamamlanan İşler:*",
        ]
        for t in report.completed_tasks:
            lines.append(f"- {t}")
        if report.carried_over_tasks:
            lines.append("")
            lines.append("*⏳ Devam Eden / Tıkanan Maddeler:*")
            for t in report.carried_over_tasks:
                lines.append(f"- {t}")
    else:
        lines = [
            f"📊 *Weekly Engineering Retrospective ({report.start_date} - {report.end_date})*",
            f"🎯 *Velocity Score:* {report.velocity_score}%",
            f"🐙 *Git Commits:* {report.total_commits}",
            "",
            "*✅ Completed Highlights:*",
        ]
        for t in report.completed_tasks:
            lines.append(f"- {t}")
        if report.carried_over_tasks:
            lines.append("")
            lines.append("*⏳ Carried Over / Open Items:*")
            for t in report.carried_over_tasks:
                lines.append(f"- {t}")

    return "\n".join(lines)
