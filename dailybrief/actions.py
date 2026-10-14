from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def copy_to_clipboard(text: str) -> bool:
    try:
        if sys.platform == "win32":
            proc = subprocess.run(["clip"], input=text, text=True, check=False)
            return proc.returncode == 0
        elif sys.platform == "darwin" and shutil.which("pbcopy"):
            proc = subprocess.run(["pbcopy"], input=text, text=True, check=False)
            return proc.returncode == 0
        elif sys.platform.startswith("linux"):
            if shutil.which("wl-copy"):
                proc = subprocess.run(["wl-copy"], input=text, text=True, check=False)
                return proc.returncode == 0
            elif shutil.which("xclip"):
                proc = subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=False)
                return proc.returncode == 0
    except (subprocess.SubprocessError, OSError):
        pass

    return False


def export_brief(brief: str, date_str: str, output_dir: Path | str | None = None) -> Path:
    target_dir = Path(output_dir) if output_dir else Path.cwd()
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"brief-{date_str}.md"
    file_path = target_dir / filename
    content = f"# Daily Brief - {date_str}\n\n{brief}\n"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def format_standup_text(brief: str, date_str: str, lang: str = "en") -> str:
    is_tr = lang.lower() == "tr"
    prefix = f"📅 *Günlük Standup ({date_str})*\n\n" if is_tr else f"📅 *Daily Standup ({date_str})*\n\n"

    # Clean any excessive blank lines while preserving bullets
    lines = [line.strip() for line in brief.splitlines() if line.strip()]
    return prefix + "\n".join(lines)


def generate_branch_name(task_text: str) -> str:
    cleaned = re.sub(r"^(?:\d+[\.\)]|[\-\*\•])\s+", "", task_text.strip()).lower()

    is_fix = any(w in cleaned for w in ("fix", "bug", "issue", "error", "patch", "sorun", "hata", "coz"))
    prefix = "fix/" if is_fix else "feat/"

    # Remove non-alphanumeric chars
    words = re.findall(r"[a-z0-9]+", cleaned)
    # Filter short stop words
    filtered = [w for w in words if w not in {"the", "a", "an", "and", "or", "in", "on", "for", "with", "bir", "ve", "icin"}]
    slug = "-".join(filtered[:5]) or "task-update"

    if len(slug) > 30:
        slug = slug[:30].rstrip("-")

    return f"{prefix}{slug}"


def checkout_branch(branch_name: str, repo_path: Path | str | None = None) -> tuple[bool, str]:
    if not shutil.which("git"):
        return False, "git command is not available."

    cwd = str(repo_path) if repo_path else "."
    try:
        proc = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return True, f"Switched to a new branch '{branch_name}'"
        err_msg = proc.stderr.strip() or proc.stdout.strip()
        return False, f"Git error: {err_msg}"
    except (subprocess.SubprocessError, OSError) as exc:
        return False, f"Failed to execute git checkout: {exc}"


def append_task_breakdown(
    breakdown_text: str,
    task_title: str,
    date_str: str,
    target_dir: Path | str | None = None,
) -> Path:
    base_dir = Path(target_dir) if target_dir else Path.cwd()
    base_dir.mkdir(parents=True, exist_ok=True)

    file_path = base_dir / f"tasks-{date_str}.md"
    entry = f"\n\n## Task: {task_title}\n\n{breakdown_text.strip()}\n"

    if file_path.exists():
        existing = file_path.read_text(encoding="utf-8")
        file_path.write_text(existing + entry, encoding="utf-8")
    else:
        file_path.write_text(f"# Task Breakdowns - {date_str}{entry}", encoding="utf-8")

    return file_path
