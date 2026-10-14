from __future__ import annotations

from pathlib import Path
import pytest

from dailybrief.cache import (
    CacheEntry,
    clear_cache,
    compute_git_hash,
    compute_notes_hash,
    compute_state_hash,
    get_cache_stats,
    get_cached_brief,
    render_cache_badge,
    save_cached_brief,
)
from dailybrief.git_context import GitContext, GitRepoSummary
from dailybrief.reader import Note


def test_compute_notes_hash_deterministic() -> None:
    notes_1 = [Note("a.md", "hello"), Note("b.txt", "world")]
    notes_2 = [Note("b.txt", "world"), Note("a.md", "hello")]  # reversed order
    notes_3 = [Note("a.md", "hello different")]

    hash_1 = compute_notes_hash(notes_1)
    hash_2 = compute_notes_hash(notes_2)
    hash_3 = compute_notes_hash(notes_3)

    assert hash_1 == hash_2
    assert hash_1 != hash_3
    assert len(hash_1) == 64


def test_compute_git_hash() -> None:
    assert compute_git_hash(None) == "no_git"

    repo = GitRepoSummary(
        path=Path("/tmp/repo"),
        name="repo",
        branch="main",
        recent_commits=["c1 commit"],
        uncommitted_count=1,
        modified_files=["app.py"],
    )
    ctx1 = GitContext(
        branch="main",
        recent_commits=["c1 commit"],
        uncommitted_count=1,
        modified_files=["app.py"],
        repos=[repo],
    )
    ctx2 = GitContext(
        branch="feature",
        recent_commits=["c2 commit"],
        uncommitted_count=0,
        modified_files=[],
        repos=[],
    )

    h1 = compute_git_hash(ctx1)
    h2 = compute_git_hash(ctx2)
    assert h1 != h2
    assert len(h1) == 64


def test_compute_state_hash() -> None:
    h = compute_state_hash("notes", "git", "anthropic", "claude-sonnet-4-6", "en", "2026-10-15")
    assert len(h) == 64
    h_same = compute_state_hash("notes", "git", "anthropic", "claude-sonnet-4-6", "en", "2026-10-15")
    assert h == h_same
    h_diff = compute_state_hash("notes", "git", "openai", "gpt-4o", "en", "2026-10-15")
    assert h != h_diff


def test_save_and_get_cached_brief(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    entry = CacheEntry(
        state_hash="a" * 64,
        date_str="2026-10-15",
        brief="Key Priorities for Today:\n1. Task 1",
        notes_count=2,
        created_at=123456789.0,
        provider="anthropic",
        model="claude-sonnet-4-6",
        lang="en",
    )

    saved_path = save_cached_brief(entry, cache_dir=cache_dir)
    assert saved_path.exists()

    loaded = get_cached_brief("a" * 64, "2026-10-15", cache_dir=cache_dir)
    assert loaded is not None
    assert loaded.brief == entry.brief
    assert loaded.provider == "anthropic"

    # Miss on different hash or date
    assert get_cached_brief("b" * 64, "2026-10-15", cache_dir=cache_dir) is None
    assert get_cached_brief("a" * 64, "2026-10-16", cache_dir=cache_dir) is None


def test_cache_stats_and_clear(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    assert get_cache_stats(cache_dir)["entries"] == 0

    entry1 = CacheEntry("1" * 64, "2026-10-15", "brief1", 1, 0.0, "p", "m", "en")
    entry2 = CacheEntry("2" * 64, "2026-10-15", "brief2", 1, 0.0, "p", "m", "en")
    save_cached_brief(entry1, cache_dir)
    save_cached_brief(entry2, cache_dir)

    stats = get_cache_stats(cache_dir)
    assert stats["entries"] == 2
    assert stats["size_bytes"] > 0

    cleared = clear_cache(cache_dir)
    assert cleared == 2
    assert get_cache_stats(cache_dir)["entries"] == 0


def test_render_cache_badge() -> None:
    badge_en = render_cache_badge("en")
    assert "0 tokens used" in badge_en.plain

    badge_tr = render_cache_badge("tr")
    assert "0 token" in badge_tr.plain
