from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class GitRepoSummary:
    path: Path
    name: str
    branch: str
    recent_commits: list[str]
    uncommitted_count: int
    modified_files: list[str]


@dataclass(frozen=True)
class GitContext:
    branch: str
    recent_commits: list[str]
    uncommitted_count: int
    modified_files: list[str]
    repos: list[GitRepoSummary] = field(default_factory=list)

    def format_banner(self, lang: str = "en") -> str:
        is_tr = lang.lower() == "tr"
        if len(self.repos) > 1:
            details = []
            for r in self.repos:
                details.append(f"{r.name} ('{r.branch}')")
            details_str = ", ".join(details)
            if is_tr:
                return f"{len(self.repos)} Git deposu izleniyor: {details_str} | Toplam {self.uncommitted_count} değişiklik"
            return f"Watching {len(self.repos)} repo(s): {details_str} | {self.uncommitted_count} uncommitted total"

        # Single repo format
        if is_tr:
            return f"'{self.branch}' dalı | Son 48 saatte {len(self.recent_commits)} commit | {self.uncommitted_count} değişiklik"
        return f"branch '{self.branch}' | {len(self.recent_commits)} commit(s) last 48h | {self.uncommitted_count} uncommitted"

    def format_for_prompt(self, lang: str = "en") -> str:
        is_tr = lang.lower() == "tr"

        if len(self.repos) > 1:
            lines: list[str] = []
            header = f"Aktif Git Depoları ({len(self.repos)} Depo):" if is_tr else f"Active Git Repositories ({len(self.repos)}):"
            lines.append(header)
            for repo in self.repos:
                r_branch = "Dal (Branch)" if is_tr else "Branch"
                r_commits = "Son Commitler (Son 48 saat)" if is_tr else "Recent Commits (Last 48h)"
                r_uncommitted = "Commit Edilmemiş Değişiklikler" if is_tr else "Uncommitted Working Changes"

                lines.append(f"• Depo / Repo '{repo.name}' ({r_branch}: {repo.branch}):")
                if repo.recent_commits:
                    lines.append(f"  {r_commits}:")
                    for c in repo.recent_commits:
                        lines.append(f"    - {c}")
                else:
                    lines.append(f"  {r_commits}: " + ("Yok" if is_tr else "None"))

                if repo.uncommitted_count > 0:
                    files_prev = ", ".join(repo.modified_files[:5])
                    count_suffix = f"{repo.uncommitted_count} dosya" if is_tr else f"{repo.uncommitted_count} file(s)"
                    lines.append(f"  {r_uncommitted}: {count_suffix} ({files_prev})")
                else:
                    lines.append(f"  {r_uncommitted}: " + ("Temiz (değişiklik yok)" if is_tr else "Clean (no changes)"))
            return "\n".join(lines)

        # Single repo backward-compatible format
        lines: list[str] = []
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


def _inspect_single_repo(path: Path) -> GitRepoSummary | None:
    cwd = str(path)
    try:
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
        commits = [line.strip() for line in log_proc.stdout.splitlines() if line.strip()]

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

        repo_name = path.resolve().name
        return GitRepoSummary(
            path=path.resolve(),
            name=repo_name,
            branch=branch,
            recent_commits=commits,
            uncommitted_count=uncommitted_count,
            modified_files=modified_files,
        )
    except (subprocess.SubprocessError, OSError):
        return None


def collect_git_context(
    repo_paths: list[Path | str] | Path | str | None = None,
) -> GitContext | None:
    if not shutil.which("git"):
        return None

    paths_to_check: list[Path] = []
    if repo_paths is None:
        paths_to_check = [Path.cwd()]
    elif isinstance(repo_paths, (str, Path)):
        paths_to_check = [Path(repo_paths)]
    else:
        paths_to_check = [Path(p) for p in repo_paths if str(p).strip()]

    if not paths_to_check:
        paths_to_check = [Path.cwd()]

    if len(paths_to_check) == 1:
        single_res = _inspect_single_repo(paths_to_check[0])
        summaries = [single_res] if single_res is not None else []
    else:
        max_workers = min(8, len(paths_to_check))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(_inspect_single_repo, paths_to_check))
        summaries = [s for s in results if s is not None]

    if not summaries:
        return None

    primary = summaries[0]
    all_commits: list[str] = []
    total_uncommitted = 0
    all_modified: list[str] = []

    for s in summaries:
        prefix = f"[{s.name}] " if len(summaries) > 1 else ""
        for c in s.recent_commits:
            all_commits.append(f"{prefix}{c}")
        total_uncommitted += s.uncommitted_count
        for mf in s.modified_files:
            all_modified.append(f"{prefix}{mf}")

    return GitContext(
        branch=primary.branch,
        recent_commits=all_commits,
        uncommitted_count=total_uncommitted,
        modified_files=all_modified,
        repos=summaries,
    )
