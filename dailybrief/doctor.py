from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

from rich.table import Table
from rich.text import Text

from dailybrief.cache import get_cache_stats
from dailybrief.config import DEFAULT_CONFIG_PATH, load_config, resolve_api_key


@dataclass(frozen=True)
class DoctorCheck:
    category: str
    name: str
    status: str  # "PASS", "WARN", "FAIL"
    details: str
    advice: str = ""


def check_config(config_path: Path | None = None) -> DoctorCheck:
    cfg_file = config_path or DEFAULT_CONFIG_PATH
    if not cfg_file.exists():
        return DoctorCheck(
            category="Config",
            name="Configuration File",
            status="WARN",
            details=f"Not found at {cfg_file} (using defaults)",
            advice="Run dailybrief once or create ~/.dailybrief/config.toml to customize.",
        )
    try:
        cfg = load_config(cfg_file)
        return DoctorCheck(
            category="Config",
            name="Configuration File",
            status="PASS",
            details=f"Loaded from {cfg_file} (provider: {cfg.provider or 'anthropic'})",
        )
    except Exception as exc:
        return DoctorCheck(
            category="Config",
            name="Configuration File",
            status="FAIL",
            details=f"Parse error: {exc}",
            advice="Inspect ~/.dailybrief/config.toml for syntax errors.",
        )


def check_provider(lang: str = "en") -> list[DoctorCheck]:
    cfg = load_config()
    provider = cfg.provider or "anthropic"
    checks: list[DoctorCheck] = []

    # 1. Active provider key
    key = resolve_api_key(provider, cfg)
    if provider == "ollama":
        # Check local Ollama reachability
        is_reachable = False
        try:
            req = urllib.request.Request("http://localhost:11434/api/version", method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    is_reachable = True
        except Exception:
            is_reachable = False

        if is_reachable:
            checks.append(
                DoctorCheck(
                    category="LLM",
                    name="Ollama Local Daemon",
                    status="PASS",
                    details="Reachable at http://localhost:11434",
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    category="LLM",
                    name="Ollama Local Daemon",
                    status="FAIL",
                    details="Cannot connect to http://localhost:11434",
                    advice="Start Ollama by running 'ollama serve' or launching the Ollama desktop app.",
                )
            )
    else:
        if key:
            masked = key[:4] + "..." + key[-4:] if len(key) >= 8 else "***"
            checks.append(
                DoctorCheck(
                    category="LLM",
                    name=f"{provider.capitalize()} API Key",
                    status="PASS",
                    details=f"Configured ({masked})",
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    category="LLM",
                    name=f"{provider.capitalize()} API Key",
                    status="FAIL",
                    details="No API key found in env or config",
                    advice=f"Set {provider.upper()}_API_KEY or configure in ~/.dailybrief/config.toml.",
                )
            )

    return checks


def check_git(lang: str = "en") -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    git_bin = shutil.which("git")
    if not git_bin:
        checks.append(
            DoctorCheck(
                category="Git",
                name="Git Executable",
                status="FAIL",
                details="git command not found in PATH",
                advice="Install git or ensure it is available in your system PATH.",
            )
        )
        return checks

    # Get git version
    try:
        proc = subprocess.run(["git", "--version"], capture_output=True, text=True, check=False)
        v_str = proc.stdout.strip() if proc.returncode == 0 else "git installed"
        checks.append(DoctorCheck(category="Git", name="Git Executable", status="PASS", details=v_str))
    except OSError:
        checks.append(DoctorCheck(category="Git", name="Git Executable", status="PASS", details="Found"))

    # Check cwd repository
    try:
        proc = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True, check=False)
        if proc.returncode == 0 and proc.stdout.strip() == "true":
            branch_proc = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=False)
            branch = branch_proc.stdout.strip() or "HEAD"
            checks.append(
                DoctorCheck(
                    category="Git",
                    name="Current Workspace Repo",
                    status="PASS",
                    details=f"Active git repository on branch '{branch}'",
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    category="Git",
                    name="Current Workspace Repo",
                    status="WARN",
                    details="Current directory is not a git repository",
                    advice="Specify repos with -g /path/to/repo or configure watched_repos.",
                )
            )
    except OSError:
        pass

    return checks


def check_notes_dir(notes_dir: Path | None = None) -> DoctorCheck:
    p = notes_dir or Path("./notes")
    if not p.exists():
        return DoctorCheck(
            category="Notes",
            name="Notes Source Directory",
            status="WARN",
            details=f"Directory does not exist: {p}",
            advice="Create ./notes or specify --source <path>.",
        )
    if not p.is_dir():
        return DoctorCheck(
            category="Notes",
            name="Notes Source Directory",
            status="FAIL",
            details=f"Path is not a directory: {p}",
        )

    count = len([f for f in p.glob("*") if f.is_file() and f.suffix.lower() in {".md", ".txt"}])
    if count == 0:
        return DoctorCheck(
            category="Notes",
            name="Notes Source Directory",
            status="WARN",
            details=f"{p} exists but has 0 .md/.txt files",
            advice="Add daily scratchpads or sprint notes to this folder.",
        )

    return DoctorCheck(
        category="Notes",
        name="Notes Source Directory",
        status="PASS",
        details=f"Found {count} .md/.txt note file(s) in {p}",
    )


def check_cache_health() -> DoctorCheck:
    stats = get_cache_stats()
    if not stats["exists"]:
        return DoctorCheck(
            category="Cache",
            name="Instant Content-Hash Cache",
            status="PASS",
            details="Cache directory clean (ready for initial run)",
        )

    entries = stats["entries"]
    size_kb = stats["size_bytes"] / 1024
    return DoctorCheck(
        category="Cache",
        name="Instant Content-Hash Cache",
        status="PASS",
        details=f"{entries} cached brief(s) ({size_kb:.1f} KB)",
    )


def check_voice_availability() -> DoctorCheck:
    cfg = load_config()
    if cfg.openai_api_key or resolve_api_key("openai", cfg):
        return DoctorCheck(
            category="Voice",
            name="Voice Briefing Engine",
            status="PASS",
            details="OpenAI TTS API ready",
        )

    # Check local system fallback
    if sys.platform == "win32":
        return DoctorCheck(
            category="Voice",
            name="Voice Briefing Engine",
            status="PASS",
            details="Windows SAPI COM Speech Synthesizer available",
        )
    elif sys.platform == "darwin" and shutil.which("say"):
        return DoctorCheck(
            category="Voice",
            name="Voice Briefing Engine",
            status="PASS",
            details="macOS native 'say' speech synthesizer available",
        )
    elif sys.platform.startswith("linux") and shutil.which("espeak"):
        return DoctorCheck(
            category="Voice",
            name="Voice Briefing Engine",
            status="PASS",
            details="Linux 'espeak' synthesizer available",
        )

    return DoctorCheck(
        category="Voice",
        name="Voice Briefing Engine",
        status="WARN",
        details="No TTS engine detected (OpenAI API key or local speech tool)",
        advice="Set OPENAI_API_KEY for studio-quality voice briefings.",
    )


def run_doctor(
    lang: str = "en",
    config_path: Path | None = None,
    notes_dir: Path | None = None,
) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    checks.append(check_config(config_path))
    checks.extend(check_provider(lang))
    checks.extend(check_git(lang))
    checks.append(check_notes_dir(notes_dir))
    checks.append(check_cache_health())
    checks.append(check_voice_availability())
    return checks


def render_doctor_table(checks: list[DoctorCheck], lang: str = "en") -> Table:
    is_tr = lang.lower() == "tr"
    title = "DailyBrief Sistem Tanılama (Doctor)" if is_tr else "DailyBrief System Diagnostics (Doctor)"
    table = Table(title=title, show_header=True, header_style="bold cyan")

    col_cat = "Kategori" if is_tr else "Category"
    col_check = "Kontrol" if is_tr else "Check"
    col_status = "Durum" if is_tr else "Status"
    col_details = "Detaylar" if is_tr else "Details"
    col_advice = "Öneri" if is_tr else "Recommendation"

    table.add_column(col_cat, style="dim")
    table.add_column(col_check, style="bold")
    table.add_column(col_status, justify="center")
    table.add_column(col_details)
    table.add_column(col_advice, style="dim italic")

    for c in checks:
        if c.status == "PASS":
            status_text = Text("✔ PASS", style="bold green")
        elif c.status == "WARN":
            status_text = Text("▲ WARN", style="bold yellow")
        else:
            status_text = Text("✘ FAIL", style="bold red")

        table.add_row(c.category, c.name, status_text, c.details, c.advice)

    return table
