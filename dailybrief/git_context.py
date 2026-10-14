from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class GitContext:
    branch: str
    recent_commits: list[str]
    uncommitted_count: int
    modified_files: list[str]

    def format_for_prompt(self, lang: str = "en") -> str:
        lines: list[str] = []
        is_tr = lang.lower() == "tr"

        branch_label = "Aktif Git Dalı (Branch)" if is_tr else "Active Git Branch"
        commits_label = "Son Git Commitleri (Son 48 saat)" if is_tr else "Recent Git Commits (Last 48h)"
        uncommitted_label = "Commit Edilmemiş Değişiklikler" if is_tr else "Uncommitted Working Changes"

        lines.append(f"{branch_label}: {self.branch}")

        if self.recent_commits:
            lines.append(f"{commits_label}:")
            for c in self.recent_commits:
                lines.append(f"  - {c}")
        else:
            lines.append(f"{commits_label}: " + ("Yok" if is_tr else "None"))

        if self.uncommitted_count > 0:
            files_preview = ", ".join(self.modified_files[:5])
            if len(self.modified_files) > 5:
                files_preview += "..."
            count_suffix = f"{self.uncommitted_count} dosya" if is_tr else f"{self.uncommitted_count} file(s)"
            lines.append(f"{uncommitted_label}: {count_suffix} ({files_preview})")
        else:
            lines.append(f"{uncommitted_label}: " + ("Temiz (değişiklik yok)" if is_tr else "Clean (no changes)"))

        return "\n".join(lines)


def collect_git_context(repo_path: Path | str | None = None) -> GitContext | None:
    if not shutil.which("git"):
        return None

    cwd = str(repo_path) if repo_path else "."

    try:
        # Check if inside git work tree
        inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return None

        # Current branch
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        branch = branch_proc.stdout.strip() or "HEAD"

        # Recent commits (last 48h, max 5)
        log_proc = subprocess.run(
            ["git", "log", "-n", "5", "--since=48 hours ago", "--pretty=format:%h %s"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        commits: list[str] = [line.strip() for line in log_proc.stdout.splitlines() if line.strip()]

        # Status porcelain
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        status_lines = [line.strip() for line in status_proc.stdout.splitlines() if line.strip()]
        uncommitted_count = len(status_lines)
        modified_files = [line.split()[-1] for line in status_lines]

        return GitContext(
            branch=branch,
            recent_commits=commits,
            uncommitted_count=uncommitted_count,
            modified_files=modified_files,
        )
    except (subprocess.SubprocessError, OSError):
        return None
