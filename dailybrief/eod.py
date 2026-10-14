from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re

from rich.panel import Panel
from rich.text import Text

from dailybrief.blockers import extract_keywords, extract_priorities_from_brief
from dailybrief.memory import HISTORY_DIR, HistoryEntry


@dataclass(frozen=True)
class ReconciledTask:
    title: str
    status: str  # "completed", "in_progress", "carried_over"
    evidence: str


@dataclass(frozen=True)
class EODSummary:
    date: str
    completed: list[ReconciledTask]
    in_progress: list[ReconciledTask]
    carried_over: list[ReconciledTask]
    total_tasks: int

    @property
    def completion_rate(self) -> float:
        if self.total_tasks == 0:
            return 100.0
        return (len(self.completed) / self.total_tasks) * 100.0


def reconcile_eod(
    morning_brief: str,
    date_str: str,
    git_commits: list[str] | None = None,
    git_modified_files: list[str] | None = None,
    note_contents: list[str] | None = None,
    lang: str = "en",
) -> EODSummary:
    tasks = extract_priorities_from_brief(morning_brief)
    is_tr = lang.lower() == "tr"

    completed: list[ReconciledTask] = []
    in_progress: list[ReconciledTask] = []
    carried_over: list[ReconciledTask] = []

    commits = git_commits or []
    modified_files = git_modified_files or []

    # Parse notes for [x] or done markers
    checked_lines: list[str] = []
    if note_contents:
        for c in note_contents:
            for line in c.splitlines():
                if re.search(r"(\[x\]|done:|tamamland[ıi]:)", line, re.IGNORECASE):
                    checked_lines.append(line.strip())

    for task in tasks:
        task_kws = extract_keywords(task)
        if not task_kws:
            carried_over.append(ReconciledTask(
                title=task,
                status="carried_over",
                evidence="Detay belirlenemedi" if is_tr else "No keywords matched",
            ))
            continue

        # 1. Check notes for [x] completion
        matched_checked = None
        for cl in checked_lines:
            cl_kws = extract_keywords(cl)
            if task_kws.intersection(cl_kws):
                matched_checked = cl
                break

        if matched_checked:
            evidence = f"Notta tamamlandı: {matched_checked[:40]}" if is_tr else f"Checked in notes: {matched_checked[:40]}"
            completed.append(ReconciledTask(title=task, status="completed", evidence=evidence))
            continue

        # 2. Check Git commits for matching messages
        matched_commit = None
        for c in commits:
            c_kws = extract_keywords(c)
            if task_kws.intersection(c_kws):
                matched_commit = c
                break

        if matched_commit:
            evidence = f"Git commit: {matched_commit}" if is_tr else f"Git commit: {matched_commit}"
            completed.append(ReconciledTask(title=task, status="completed", evidence=evidence))
            continue

        # 3. Check uncommitted working files for active work
        matched_mod = None
        for mf in modified_files:
            mf_kws = extract_keywords(mf)
            if task_kws.intersection(mf_kws):
                matched_mod = mf
                break

        if matched_mod:
            evidence = f"Değiştirilen dosya: {matched_mod}" if is_tr else f"Modified file: {matched_mod}"
            in_progress.append(ReconciledTask(title=task, status="in_progress", evidence=evidence))
            continue

        # 4. If no activity found -> Carried Over
        evidence = "Bugün dokunulmadı" if is_tr else "Untouched today"
        carried_over.append(ReconciledTask(title=task, status="carried_over", evidence=evidence))

    return EODSummary(
        date=date_str,
        completed=completed,
        in_progress=in_progress,
        carried_over=carried_over,
        total_tasks=len(tasks),
    )


def render_eod_panel(eod: EODSummary, lang: str = "en") -> Panel:
    is_tr = lang.lower() == "tr"
    title = f"🌙 Gün Sonu Kapanışı ({eod.date})" if is_tr else f"🌙 End-of-Day Wrap-Up ({eod.date})"

    body = Text()

    # Section 1: Completed
    body.append("✅ " + ("Bugün Tamamlananlar" if is_tr else "Completed Today") + f" ({len(eod.completed)})\n", style="bold green")
    if eod.completed:
        for t in eod.completed:
            body.append(f"  • {t.title}\n", style="green")
            body.append(f"    ↳ {t.evidence}\n", style="dim")
    else:
        body.append("  " + ("(Kayıtlı tamamlanan iş yok)" if is_tr else "(No completed tasks recorded)") + "\n", style="dim")
    body.append("\n")

    # Section 2: In Progress
    body.append("🔄 " + ("Devam Edenler / Yarım Kalanlar" if is_tr else "In Progress / Active Work") + f" ({len(eod.in_progress)})\n", style="bold yellow")
    if eod.in_progress:
        for t in eod.in_progress:
            body.append(f"  • {t.title}\n", style="yellow")
            body.append(f"    ↳ {t.evidence}\n", style="dim")
    else:
        body.append("  " + ("(Yarım kalan iş yok)" if is_tr else "(No tasks currently in progress)") + "\n", style="dim")
    body.append("\n")

    # Section 3: Carried Over
    body.append("⏭️ " + ("Yarına Devredenler" if is_tr else "Carried Over to Tomorrow") + f" ({len(eod.carried_over)})\n", style="bold magenta")
    if eod.carried_over:
        for t in eod.carried_over:
            body.append(f"  • {t.title}\n", style="magenta")
            body.append(f"    ↳ {t.evidence}\n", style="dim")
    else:
        body.append("  " + ("(Devreden iş yok, harika!)" if is_tr else "(All planned tasks touched!)") + "\n", style="dim")
    body.append("\n")

    # Footer stats
    stats_label = "Tamamlama Oranı" if is_tr else "Completion Rate"
    body.append(f"🎯 {stats_label}: {len(eod.completed)}/{eod.total_tasks} ({eod.completion_rate:.0f}%)", style="bold cyan")

    return Panel(body, title=title, border_style="cyan", padding=(1, 2))


def format_eod_standup(eod: EODSummary, lang: str = "en") -> str:
    is_tr = lang.lower() == "tr"
    lines: list[str] = []

    header = f"🌙 *Gün Sonu Özeti ({eod.date})*" if is_tr else f"🌙 *End-of-Day Update ({eod.date})*"
    lines.append(header)
    lines.append("")

    lines.append("✅ *" + ("Tamamlananlar:" if is_tr else "Completed Today:") + "*")
    if eod.completed:
        for t in eod.completed:
            lines.append(f"- {t.title}")
    else:
        lines.append("- " + ("Tamamlanan iş yok" if is_tr else "None"))
    lines.append("")

    lines.append("🔄 *" + ("Devam Edenler:" if is_tr else "In Progress:") + "*")
    if eod.in_progress:
        for t in eod.in_progress:
            lines.append(f"- {t.title} ({t.evidence})")
    else:
        lines.append("- " + ("Yok" if is_tr else "None"))
    lines.append("")

    lines.append("⏭️ *" + ("Yarına Devredenler:" if is_tr else "Carried Over to Tomorrow:") + "*")
    if eod.carried_over:
        for t in eod.carried_over:
            lines.append(f"- {t.title}")
    else:
        lines.append("- " + ("Yok" if is_tr else "None"))

    lines.append("")
    lines.append(f"🎯 Progress: {len(eod.completed)}/{eod.total_tasks} ({eod.completion_rate:.0f}%)")

    return "\n".join(lines)


def save_eod_summary(
    eod: EODSummary,
    history_dir: Path | None = None,
) -> Path:
    target_dir = history_dir or HISTORY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / f"{eod.date}-eod.json"
    data = {
        "date": eod.date,
        "completed": [asdict(t) for t in eod.completed],
        "in_progress": [asdict(t) for t in eod.in_progress],
        "carried_over": [asdict(t) for t in eod.carried_over],
        "total_tasks": eod.total_tasks,
        "completion_rate": eod.completion_rate,
    }
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path
