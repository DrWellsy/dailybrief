from __future__ import annotations

from pathlib import Path

from dailybrief.todo_scanner import (
    TodoItem,
    _clean_comment,
    _parse_todo_line,
    format_todos_for_prompt,
    scan_codebase_todos,
)


def test_clean_comment():
    assert _clean_comment("// TODO: Fix this bug") == "Fix this bug"
    assert _clean_comment("# FIXME: Urgent refactor") == "Urgent refactor"
    assert _clean_comment("/* HACK: Temporary workaround */") == "Temporary workaround"
    assert _clean_comment("-- TODO: SQL migration pending") == "SQL migration pending"


def test_parse_todo_line():
    parsed = _parse_todo_line("  // TODO: Add oauth2 refresh token")
    assert parsed is not None
    assert parsed[0] == "TODO"
    assert parsed[1] == "Add oauth2 refresh token"

    parsed_fixme = _parse_todo_line("/* FIXME(security): prevent sql injection */")
    assert parsed_fixme is not None
    assert parsed_fixme[0] == "FIXME"
    assert "prevent sql injection" in parsed_fixme[1]

    # No tag
    assert _parse_todo_line("const x = 42;") is None


def test_format_todos_for_prompt():
    todos = [
        TodoItem(file_path="src/auth.py", line_num=42, tag="FIXME", comment="Fix token expiry", is_recent=True),
        TodoItem(file_path="api/routes.py", line_num=105, tag="TODO", comment="Add rate limiting"),
    ]

    en_text = format_todos_for_prompt(todos, lang="en")
    assert "CODEBASE INLINE TODOS & FIXMES:" in en_text
    assert "- [FIXME] src/auth.py:42 - Fix token expiry [Recent]" in en_text
    assert "- [TODO] api/routes.py:105 - Add rate limiting" in en_text

    tr_text = format_todos_for_prompt(todos, lang="tr")
    assert "KOD İÇİ GÖREVLER (TODO / FIXME / HACK):" in tr_text


def test_scan_codebase_todos_filesystem_fallback(tmp_path: Path):
    sub = tmp_path / "src"
    sub.mkdir()
    code_file = sub / "service.py"
    code_file.write_text(
        "# Regular comment\n"
        "def compute():\n"
        "    # FIXME: handle division by zero\n"
        "    # TODO: optimize memory cache\n"
        "    return 100\n",
        encoding="utf-8",
    )

    ignored_dir = tmp_path / "node_modules"
    ignored_dir.mkdir()
    (ignored_dir / "dep.js").write_text("// TODO: should be ignored", encoding="utf-8")

    items = scan_codebase_todos(repos=[tmp_path], max_items=10)
    assert len(items) == 2
    tags = [i.tag for i in items]
    assert "FIXME" in tags
    assert "TODO" in tags
    # Ensure node_modules was ignored
    assert not any("node_modules" in i.file_path for i in items)


def test_scan_codebase_todos_prioritizes_recent(tmp_path: Path):
    f1 = tmp_path / "file1.py"
    f1.write_text("# TODO: task one\n", encoding="utf-8")
    f2 = tmp_path / "file2.py"
    f2.write_text("# TODO: task two\n", encoding="utf-8")

    items = scan_codebase_todos(
        repos=[tmp_path],
        git_modified_files=["file2.py"],
        max_items=10,
    )
    assert len(items) == 2
    assert items[0].file_path.endswith("file2.py")
    assert items[0].is_recent is True
