from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess

from rich.panel import Panel
from rich.text import Text


@dataclass(frozen=True)
class GitRadarAlert:
    repo_name: str
    upstream_branch: str
    behind_count: int
    ahead_count: int
    conflicting_files: list[str]
    upstream_commits: list[str]
    advice: str


def _get_upstream_branch(cwd: str) -> str | None:
    # 1. Try tracking branch @{u}
    proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        timeout=3,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()

    # 2. Try origin/main or origin/master
    for candidate in ("origin/main", "origin/master"):
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", candidate],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        if probe.returncode == 0:
            return candidate

    return None


def inspect_single_repo_radar(
    repo_path: Path,
    local_modified_files: list[str] | None = None,
    referenced_files: list[str] | None = None,
    lang: str = "en",
) -> GitRadarAlert | None:
    if not shutil.which("git"):
        return None

    cwd = str(repo_path)
    is_tr = lang.lower() == "tr"

    try:
        # Check if inside git repo
        check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        if check.returncode != 0 or check.stdout.strip() != "true":
            return None

        upstream = _get_upstream_branch(cwd)
        if not upstream:
            return None

        # Check ahead/behind divergence count
        count_proc = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", f"HEAD...{upstream}"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=4,
        )
        if count_proc.returncode != 0:
            return None

        counts = count_proc.stdout.strip().split()
        if len(counts) != 2:
            return None

        ahead = int(counts[0])
        behind = int(counts[1])

        if behind == 0:
            return None

        # Get list of files modified upstream
        diff_proc = subprocess.run(
            ["git", "diff", "--name-only", f"HEAD..{upstream}"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=4,
        )
        upstream_files = [f.strip() for f in diff_proc.stdout.splitlines() if f.strip()]

        # Check overlap with local uncommitted files or referenced note files
        local_targets = set(local_modified_files or [])
        if referenced_files:
            local_targets.update(referenced_files)

        overlapping = [f for f in upstream_files if any(lt in f or f in lt for lt in local_targets)]

        # Get recent upstream commit summaries
        log_proc = subprocess.run(
            ["git", "log", f"HEAD..{upstream}", "--oneline", "-n", "3"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=4,
        )
        upstream_commits = [c.strip() for c in log_proc.stdout.splitlines() if c.strip()]

        repo_name = repo_path.resolve().name
        if overlapping:
            if is_tr:
                advice = (
                    f"'{upstream}' dalı {behind} commit ileride ve üzerinde çalıştığınız şu dosyalarda çakışma riski var: "
                    f"{', '.join(overlapping[:3])}. Kod yazmadan önce 'git pull --rebase' yapmanız önerilir."
                )
            else:
                advice = (
                    f"Upstream '{upstream}' is ahead by {behind} commit(s) with overlapping changes in: "
                    f"{', '.join(overlapping[:3])}. Recommended action: 'git pull --rebase' before continuing."
                )
        else:
            if is_tr:
                advice = (
                    f"'{upstream}' dalında {behind} yeni commit var. Henüz çakışma tespit edilmedi ancak senkronize kalmak için çekmeniz önerilir."
                )
            else:
                advice = (
                    f"Upstream '{upstream}' has {behind} new commit(s). No overlapping files yet, but pull recommended to stay in sync."
                )

        return GitRadarAlert(
            repo_name=repo_name,
            upstream_branch=upstream,
            behind_count=behind,
            ahead_count=ahead,
            conflicting_files=overlapping,
            upstream_commits=upstream_commits,
            advice=advice,
        )
    except (subprocess.SubprocessError, OSError, ValueError):
        return None


def inspect_git_radar(
    repo_paths: list[Path | str] | Path | str | None = None,
    local_modified_files: list[str] | None = None,
    note_contents: list[str] | None = None,
    lang: str = "en",
) -> list[GitRadarAlert]:
    paths: list[Path] = []
    if repo_paths is None:
        paths = [Path.cwd()]
    elif isinstance(repo_paths, (str, Path)):
        paths = [Path(repo_paths)]
    else:
        paths = [Path(p) for p in repo_paths if str(p).strip()]

    # Extract any source file names referenced in notes (e.g. `cli.py`, `auth.ts`)
    referenced: list[str] = []
    if note_contents:
        for c in note_contents:
            found = re.findall(r"[\w\-/]+\.(?:py|js|ts|tsx|jsx|go|rs|cpp|h|json|toml|md)", c)
            referenced.extend(found)

    if len(paths) == 1:
        alert = inspect_single_repo_radar(
            repo_path=paths[0],
            local_modified_files=local_modified_files,
            referenced_files=referenced,
            lang=lang,
        )
        return [alert] if alert is not None else []

    from concurrent.futures import ThreadPoolExecutor

    def _check(p: Path) -> GitRadarAlert | None:
        return inspect_single_repo_radar(
            repo_path=p,
            local_modified_files=local_modified_files,
            referenced_files=referenced,
            lang=lang,
        )

    with ThreadPoolExecutor(max_workers=min(8, len(paths))) as executor:
        results = list(executor.map(_check, paths))

    return [a for a in results if a is not None]


def render_radar_panel(alerts: list[GitRadarAlert], lang: str = "en") -> Panel | None:
    if not alerts:
        return None

    is_tr = lang.lower() == "tr"
    title = "⚡ Git Radarı / Çakışma Riski" if is_tr else "⚡ Git Radar / Upstream Conflict Warning"

    body = Text()
    for idx, a in enumerate(alerts, start=1):
        has_overlap = bool(a.conflicting_files)
        status_color = "bold red" if has_overlap else "bold yellow"

        body.append(f"• Depo / Repo '{a.repo_name}' ", style=status_color)
        body.append(f"(vs {a.upstream_branch}): {a.behind_count} commit arkada / behind\n", style="dim")

        if a.conflicting_files:
            risk_label = "Çakışma Riski Olan Dosyalar" if is_tr else "Overlapping Files"
            body.append(f"  ⚠️ {risk_label}: {', '.join(a.conflicting_files)}\n", style="red")

        if a.upstream_commits:
            commits_label = "Son Upstream Commitleri" if is_tr else "Recent Upstream Commits"
            body.append(f"  ↳ {commits_label}:\n", style="dim")
            for c in a.upstream_commits[:2]:
                body.append(f"    - {c}\n", style="dim")

        body.append(f"  💡 {a.advice}\n", style="cyan")
        if idx < len(alerts):
            body.append("\n")

    return Panel(body, title=title, border_style="yellow", padding=(1, 2))
