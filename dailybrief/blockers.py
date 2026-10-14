from __future__ import annotations

from dataclasses import dataclass
import re

from rich.panel import Panel
from rich.text import Text

from dailybrief.memory import HistoryEntry

STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "have", "before", "after",
    "today", "will", "your", "into", "over", "some", "more", "then", "them", "about",
    "bugun", "icin", "ile", "veya", "olan", "daha", "kadar", "once", "sonra", "gore",
    "gibi", "bunu", "buna", "tane", "gunluk", "gorev", "task", "item", "must", "need"
}


@dataclass(frozen=True)
class BlockerAlert:
    task: str
    streak_days: int
    advice: str


def extract_keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
    return {w for w in words if len(w) >= 3 and w not in STOP_WORDS}


def are_tasks_similar(task1: str, task2: str) -> bool:
    kw1 = extract_keywords(task1)
    kw2 = extract_keywords(task2)
    if not kw1 or not kw2:
        return False
    intersection = kw1.intersection(kw2)
    # If 2 or more significant keywords match, or >= 40% overlap
    if len(intersection) >= 2:
        return True
    overlap = len(intersection) / min(len(kw1), len(kw2))
    return overlap >= 0.4


def extract_priorities_from_brief(brief_text: str) -> list[str]:
    priorities: list[str] = []
    lines = brief_text.splitlines()
    in_priorities = False

    for line in lines:
        cleaned = line.strip()
        lower = cleaned.lower()

        # Check section boundaries
        priority_headers = (
            "key priorities",
            "priorities for today",
            "today's priorities",
            "priority tasks",
            "priorities",
            "bugün öncelikli",
            "bugun oncelikli",
            "günün öncelikleri",
            "gunun oncelikleri",
            "öncelikli maddeler",
            "oncelikli maddeler",
            "öncelikler",
            "oncelikler",
        )
        closing_headers = (
            "things not to forget",
            "unutulmaması",
            "unutulmamasi",
            "follow-ups",
            "follow ups",
            "hatırlatmalar",
            "hatirlatmalar",
            "takip edilecekler",
        )
        if any(h in lower for h in priority_headers):
            in_priorities = True
            continue
        elif any(h in lower for h in closing_headers):
            if in_priorities:
                break

        if in_priorities:
            # Match lines starting with 1., 1), -, *, •
            m = re.match(r"^(?:\d+[\.\)]|[\-\*\•])\s+(.+)$", cleaned)
            if m:
                item = m.group(1).strip()
                if item:
                    priorities.append(item)

    return priorities


def detect_blockers(
    history_entries: list[HistoryEntry],
    git_commits: list[str] | None = None,
    git_modified_files: list[str] | None = None,
    note_contents: list[str] | None = None,
    lang: str = "en",
) -> list[BlockerAlert]:
    if len(history_entries) < 2:
        return []

    # History entries are sorted descending by date:
    # index 0 is yesterday, index 1 is 2 days ago, etc.
    yesterday_brief = history_entries[0].brief
    yesterday_tasks = extract_priorities_from_brief(yesterday_brief)
    if not yesterday_tasks:
        return []

    # Aggregate git activity keywords
    git_text = " ".join((git_commits or []) + (git_modified_files or [])).lower()
    git_keywords = extract_keywords(git_text)

    # Check note completion markers (e.g. [x] task or DONE: task)
    completed_text = ""
    if note_contents:
        for c in note_contents:
            for line in c.splitlines():
                if re.search(r"(\[x\]|done:|tamamland[ıi]:)", line, re.IGNORECASE):
                    completed_text += " " + line.lower()
    completed_keywords = extract_keywords(completed_text)

    is_tr = lang.lower() == "tr"
    blockers: list[BlockerAlert] = []

    for task in yesterday_tasks:
        task_kws = extract_keywords(task)
        if not task_kws:
            continue

        # Check streak across preceding history entries
        streak = 1
        for past_entry in history_entries[1:]:
            past_tasks = extract_priorities_from_brief(past_entry.brief)
            if any(are_tasks_similar(task, past_t) for past_t in past_tasks):
                streak += 1
            else:
                break

        # A task is flagged as chronic blocker if streak >= 2
        if streak >= 2:
            # Did developer make git progress on this task?
            has_git_progress = bool(task_kws.intersection(git_keywords))
            is_marked_done = bool(task_kws.intersection(completed_keywords))

            if not has_git_progress and not is_marked_done:
                if is_tr:
                    advice = (
                        f"Bu görev son {streak} gündür brifinglerde devrediyor ve ilgili Git aktivitesi yok. "
                        "Tavsiye: Görevi 15 dakikalık ilk alt adıma bölün veya engelleyen sebebi netleştirin."
                    )
                else:
                    advice = (
                        f"This task has appeared across {streak} consecutive briefings with zero related git commits. "
                        "Action: Break down into an initial 15-minute subtask or file a GitHub blocker issue."
                    )
                blockers.append(BlockerAlert(task=task, streak_days=streak, advice=advice))

    return blockers


def render_blocker_panel(blockers: list[BlockerAlert], lang: str = "en") -> Panel | None:
    if not blockers:
        return None

    is_tr = lang.lower() == "tr"
    title = "⚠️ Tıkanıklık / Devreden Görev Uyarısı" if is_tr else "⚠️ Blocker / Carry-Over Alert"

    body = Text()
    for idx, b in enumerate(blockers, start=1):
        streak_text = f"[{b.streak_days} gündür devrediyor]" if is_tr else f"[{b.streak_days} days carried over]"
        body.append(f"{idx}. {b.task} ", style="bold yellow")
        body.append(f"{streak_text}\n", style="bold red")
        body.append(f"   💡 {b.advice}\n", style="dim")
        if idx < len(blockers):
            body.append("\n")

    return Panel(body, title=title, border_style="yellow", padding=(1, 2))
