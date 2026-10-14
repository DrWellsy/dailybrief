from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


HISTORY_DIR = Path.home() / ".dailybrief" / "history"


@dataclass(frozen=True)
class HistoryEntry:
    date: str
    brief: str
    lang: str
    notes_count: int


def save_history_entry(
    brief: str,
    date_str: str,
    lang: str,
    notes_count: int,
    history_dir: Path | None = None,
) -> Path:
    target_dir = history_dir or HISTORY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    entry = HistoryEntry(
        date=date_str,
        brief=brief.strip(),
        lang=lang,
        notes_count=notes_count,
    )
    file_path = target_dir / f"{date_str}.json"
    file_path.write_text(json.dumps(asdict(entry), ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def load_recent_history(
    days: int = 2,
    exclude_date: str | None = None,
    history_dir: Path | None = None,
) -> list[HistoryEntry]:
    target_dir = history_dir or HISTORY_DIR
    if not target_dir.exists():
        return []

    entries: list[HistoryEntry] = []
    for file_path in target_dir.glob("*.json"):
        date_name = file_path.stem
        if exclude_date and date_name == exclude_date:
            continue

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            entries.append(
                HistoryEntry(
                    date=data.get("date", date_name),
                    brief=data.get("brief", ""),
                    lang=data.get("lang", "en"),
                    notes_count=int(data.get("notes_count", 0)),
                )
            )
        except (json.JSONDecodeError, OSError, ValueError):
            continue

    # Sort descending by date
    entries.sort(key=lambda e: e.date, reverse=True)
    return entries[:days]


def format_history_for_prompt(entries: list[HistoryEntry], lang: str = "en") -> str:
    if not entries:
        return ""

    is_tr = lang.lower() == "tr"
    blocks: list[str] = []

    for entry in entries:
        header = f"Önceki Günün Brifingi ({entry.date}):" if is_tr else f"Previous Briefing from {entry.date}:"
        blocks.append(f"{header}\n{entry.brief}")

    return "\n\n".join(blocks)
