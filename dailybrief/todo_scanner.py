from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess

from dailybrief.i18n import DEFAULT_LANG

IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
}

SUPPORTED_CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".md",
    ".sh",
}

TAG_REGEX = re.compile(r"\b(TODO|FIXME|HACK|XXX)(?:\((?:[^)]+)\))?\s*[:\-]?\s*(.+)", re.IGNORECASE)


@dataclass(frozen=True)
class TodoItem:
    file_path: str
    line_num: int
    tag: str
    comment: str
    repo: str | None = None
    is_recent: bool = False

    def format_line(self) -> str:
        tag_upper = self.tag.upper()
        prefix = f"{self.repo}:" if self.repo else ""
        recent_badge = " [Recent]" if self.is_recent else ""
        return f"- [{tag_upper}] {prefix}{self.file_path}:{self.line_num} - {self.comment}{recent_badge}"


def _clean_comment(raw_text: str) -> str:
    cleaned = re.sub(r"^(?:(?://|#|/\*|\*|\*/|--)\s*)+", "", raw_text.strip())
    cleaned = re.sub(r"^(?:TODO|FIXME|HACK|XXX)(?:\([^)]+\))?\s*[:\-]?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*(?:\*/)\s*$", "", cleaned).strip()
    return cleaned


def _parse_todo_line(line: str) -> tuple[str, str] | None:
    m = TAG_REGEX.search(line)
    if not m:
        return None
    tag = m.group(1).upper()
    raw_comment = m.group(2)
    comment = _clean_comment(raw_comment)
    if not comment or len(comment) < 3:
        return None
    return tag, comment


def _scan_repo_with_git(
    repo_dir: Path,
    modified_files: set[str],
    repo_name: str | None = None,
) -> list[TodoItem]:
    if not shutil.which("git"):
        return []

    items: list[TodoItem] = []
    cmd = [
        "git",
        "grep",
        "-n",
        "-I",
        "-E",
        r"\b(TODO|FIXME|HACK|XXX)\b",
        "--",
        ":(exclude)*.min.js",
        ":(exclude)*.lock",
        ":(exclude)package-lock.json",
        ":(exclude)node_modules",
        ":(exclude).venv",
        ":(exclude)dist",
        ":(exclude)build",
        ":(exclude)target",
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if proc.returncode != 0:
            return []

        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(":", 2)
            if len(parts) >= 3:
                fpath, line_str, content = parts[0], parts[1], parts[2]
                if not line_str.isdigit():
                    continue
                parsed = _parse_todo_line(content)
                if parsed:
                    tag, comment = parsed
                    line_num = int(line_str)
                    is_rec = fpath in modified_files or any(m.endswith(fpath) for m in modified_files)
                    items.append(
                        TodoItem(
                            file_path=fpath,
                            line_num=line_num,
                            tag=tag,
                            comment=comment,
                            repo=repo_name,
                            is_recent=is_rec,
                        )
                    )
    except Exception:
        pass

    return items


def _scan_repo_with_filesystem(
    repo_dir: Path,
    modified_files: set[str],
    repo_name: str | None = None,
    max_scan_files: int = 100,
) -> list[TodoItem]:
    items: list[TodoItem] = []
    files_scanned = 0

    try:
        for file_path in repo_dir.rglob("*"):
            if files_scanned >= max_scan_files:
                break
            if not file_path.is_file():
                continue
            if any(part in IGNORE_DIRS for part in file_path.parts):
                continue
            if file_path.suffix.lower() not in SUPPORTED_CODE_EXTENSIONS:
                continue

            files_scanned += 1
            rel_path = str(file_path.relative_to(repo_dir)).replace("\\", "/")
            is_rec = rel_path in modified_files or any(m.endswith(rel_path) for m in modified_files)

            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                for line_idx, line in enumerate(content.splitlines(), start=1):
                    parsed = _parse_todo_line(line)
                    if parsed:
                        tag, comment = parsed
                        items.append(
                            TodoItem(
                                file_path=rel_path,
                                line_num=line_idx,
                                tag=tag,
                                comment=comment,
                                repo=repo_name,
                                is_recent=is_rec,
                            )
                        )
            except Exception:
                continue
    except Exception:
        pass

    return items


def scan_codebase_todos(
    repos: list[Path | str] | None = None,
    max_items: int = 15,
    git_modified_files: list[str] | None = None,
) -> list[TodoItem]:
    """Scans watched repositories for inline TODO, FIXME, and HACK comments."""
    target_dirs: list[Path] = []
    if repos:
        for r in repos:
            p = Path(r)
            if p.is_dir():
                target_dirs.append(p)
    else:
        target_dirs.append(Path.cwd())

    modified_set = set(git_modified_files or [])
    all_todos: list[TodoItem] = []

    for r_dir in target_dirs:
        repo_name = r_dir.name if len(target_dirs) > 1 else None

        # 1. Try git grep
        items = _scan_repo_with_git(r_dir, modified_set, repo_name)
        # 2. Fallback to filesystem scan if git grep returned nothing or failed
        if not items:
            items = _scan_repo_with_filesystem(r_dir, modified_set, repo_name)

        all_todos.extend(items)

    # Sort: recent files first, then FIXME/HACK before TODO
    tag_weights = {"FIXME": 0, "HACK": 1, "XXX": 2, "TODO": 3}
    all_todos.sort(
        key=lambda item: (
            0 if item.is_recent else 1,
            tag_weights.get(item.tag, 4),
            item.file_path,
            item.line_num,
        )
    )

    return all_todos[:max_items]


def format_todos_for_prompt(todos: list[TodoItem], lang: str = DEFAULT_LANG) -> str:
    """Formats harvested TODO/FIXME items for inclusion in LLM prompt context."""
    if not todos:
        return ""

    is_tr = (lang or DEFAULT_LANG).lower() == "tr"
    header = (
        "KOD İÇİ GÖREVLER (TODO / FIXME / HACK):"
        if is_tr
        else "CODEBASE INLINE TODOS & FIXMES:"
    )

    lines = [item.format_line() for item in todos]
    return f"{header}\n" + "\n".join(lines)
