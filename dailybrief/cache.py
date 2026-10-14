from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any

from rich.text import Text

from dailybrief.git_context import GitContext
from dailybrief.reader import Note

CACHE_DIR = Path.home() / ".dailybrief" / "cache"


@dataclass(frozen=True)
class CacheEntry:
    state_hash: str
    date_str: str
    brief: str
    notes_count: int
    created_at: float
    provider: str
    model: str
    lang: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CacheEntry:
        return cls(
            state_hash=str(data.get("state_hash", "")),
            date_str=str(data.get("date_str", "")),
            brief=str(data.get("brief", "")),
            notes_count=int(data.get("notes_count", 0)),
            created_at=float(data.get("created_at", 0.0)),
            provider=str(data.get("provider", "")),
            model=str(data.get("model", "")),
            lang=str(data.get("lang", "en")),
        )


def compute_notes_hash(notes: list[Note]) -> str:
    hasher = hashlib.sha256()
    # Sort notes deterministically by name
    for note in sorted(notes, key=lambda n: n.name.casefold()):
        hasher.update(note.name.encode("utf-8"))
        hasher.update(b"\x00")
        hasher.update(note.content.encode("utf-8"))
        hasher.update(b"\xff")
    return hasher.hexdigest()


def compute_git_hash(git_context: GitContext | None) -> str:
    if git_context is None:
        return "no_git"

    hasher = hashlib.sha256()
    hasher.update(git_context.branch.encode("utf-8"))
    hasher.update(str(git_context.uncommitted_count).encode("utf-8"))

    for c in git_context.recent_commits:
        hasher.update(c.encode("utf-8"))
    for f in git_context.modified_files:
        hasher.update(f.encode("utf-8"))

    for r in git_context.repos:
        hasher.update(r.name.encode("utf-8"))
        hasher.update(r.branch.encode("utf-8"))
        hasher.update(str(r.uncommitted_count).encode("utf-8"))
        for rc in r.recent_commits:
            hasher.update(rc.encode("utf-8"))
        for mf in r.modified_files:
            hasher.update(mf.encode("utf-8"))

    return hasher.hexdigest()


def compute_state_hash(
    notes_hash: str,
    git_hash: str,
    provider: str,
    model: str,
    lang: str,
    date_str: str,
) -> str:
    combined = f"{notes_hash}:{git_hash}:{provider}:{model}:{lang}:{date_str}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def get_cached_brief(
    state_hash: str,
    date_str: str,
    cache_dir: Path | None = None,
) -> CacheEntry | None:
    target_dir = cache_dir or CACHE_DIR
    cache_file = target_dir / f"{date_str}_{state_hash[:16]}.json"

    if not cache_file.exists():
        return None

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        entry = CacheEntry.from_dict(data)
        if entry.state_hash == state_hash and entry.date_str == date_str:
            return entry
    except (json.JSONDecodeError, OSError, ValueError):
        return None

    return None


def save_cached_brief(
    entry: CacheEntry,
    cache_dir: Path | None = None,
) -> Path:
    target_dir = cache_dir or CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    cache_file = target_dir / f"{entry.date_str}_{entry.state_hash[:16]}.json"
    cache_file.write_text(json.dumps(entry.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return cache_file


def clear_cache(cache_dir: Path | None = None) -> int:
    target_dir = cache_dir or CACHE_DIR
    if not target_dir.exists():
        return 0

    count = 0
    for item in target_dir.glob("*.json"):
        try:
            item.unlink()
            count += 1
        except OSError:
            pass
    return count


def get_cache_stats(cache_dir: Path | None = None) -> dict[str, Any]:
    target_dir = cache_dir or CACHE_DIR
    if not target_dir.exists():
        return {"exists": False, "entries": 0, "size_bytes": 0, "path": str(target_dir)}

    entries = list(target_dir.glob("*.json"))
    total_size = sum(f.stat().st_size for f in entries if f.is_file())
    return {
        "exists": True,
        "entries": len(entries),
        "size_bytes": total_size,
        "path": str(target_dir),
    }


def render_cache_badge(lang: str = "en") -> Text:
    if lang.lower() == "tr":
        return Text("⚡ Anlık önbellekten yüklendi (0 token kullanıldı)", style="bold green")
    return Text("⚡ Loaded from instant cache (0 tokens used)", style="bold green")
