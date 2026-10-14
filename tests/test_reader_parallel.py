from __future__ import annotations

from pathlib import Path
import pytest

from dailybrief.git_context import collect_git_context
from dailybrief.reader import Note, read_notes


def test_read_notes_parallel(tmp_path: Path) -> None:
    # Create 8 different notes with different contents
    expected_notes = []
    for i in range(8):
        file_name = f"note_{i:02d}.md"
        content = f"Content for note {i}\n- Task {i}.1\n- Task {i}.2"
        (tmp_path / file_name).write_text(content, encoding="utf-8")
        expected_notes.append((file_name, content))

    notes = read_notes(tmp_path)
    assert len(notes) == 8

    # Assert strict deterministic alphabetical sorting
    for idx, (expected_name, expected_content) in enumerate(expected_notes):
        assert notes[idx].name == expected_name
        assert notes[idx].content.replace("\r\n", "\n") == expected_content


def test_read_notes_parallel_with_faulty_file(tmp_path: Path) -> None:
    (tmp_path / "note_01.md").write_text("Valid 1", encoding="utf-8")
    (tmp_path / "note_02_bad.bin.md").write_bytes(b"\x00\xff\xfe\x00")
    (tmp_path / "note_03.md").write_text("Valid 3", encoding="utf-8")

    with pytest.warns(UserWarning, match="Dosya okunamadi, atlandi"):
        notes = read_notes(tmp_path)

    assert len(notes) == 2
    assert notes[0].name == "note_01.md"
    assert notes[1].name == "note_03.md"


def test_collect_git_context_multi_repo_parallel(tmp_path: Path) -> None:
    # Create two temporary directories that are not git repos
    repo1 = tmp_path / "repo1"
    repo2 = tmp_path / "repo2"
    repo1.mkdir()
    repo2.mkdir()

    # When inspecting non-git directories, collect_git_context handles them in parallel and returns None
    res = collect_git_context([repo1, repo2])
    assert res is None
