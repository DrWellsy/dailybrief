from __future__ import annotations

from datetime import date
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

from dailybrief.config import DEFAULT_CONFIG_PATH, load_config, resolve_api_key
from dailybrief.i18n import get_message
from dailybrief.providers import get_provider


def validate_time_str(time_str: str) -> tuple[int, int]:
    m = re.match(r"^(\d{1,2}):(\d{2})$", time_str.strip())
    if not m:
        raise ValueError(f"Invalid time format: '{time_str}'. Expected HH:MM (e.g. 08:45, 09:00).")
    hour, minute = int(m.group(1)), int(m.group(2))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid time range: '{time_str}'. Hour must be 0-23, minute 0-59.")
    return hour, minute


def get_dailybrief_executable_command() -> str:
    # If running inside a PyInstaller frozen binary
    if getattr(sys, "frozen", False) and hasattr(sys, "executable"):
        return f'"{sys.executable}" --background'

    # Otherwise, use python executable + module
    py_exec = sys.executable
    return f'"{py_exec}" -m dailybrief.cli --background'


def schedule_daily_task(time_str: str, lang: str = "en") -> tuple[bool, str]:
    try:
        hour, minute = validate_time_str(time_str)
    except ValueError as exc:
        return False, str(exc)

    formatted_time = f"{hour:02d}:{minute:02d}"
    cmd = get_dailybrief_executable_command()

    if sys.platform == "win32":
        task_name = "DailyBriefMorning"
        # schtasks /create /tn DailyBriefMorning /tr "..." /sc daily /st HH:MM /f
        sch_cmd = [
            "schtasks",
            "/create",
            "/tn",
            task_name,
            "/tr",
            cmd,
            "/sc",
            "daily",
            "/st",
            formatted_time,
            "/f",
        ]
        try:
            proc = subprocess.run(sch_cmd, capture_output=True, text=True, check=False)
            if proc.returncode == 0:
                msg = (
                    f"Otomatik sabah brifingi her gün saat {formatted_time} için zamanlandı (Windows Görev Zamanlayıcı: {task_name})."
                    if lang.lower() == "tr"
                    else f"Autonomous morning briefing scheduled daily at {formatted_time} (Windows Task: {task_name})."
                )
                return True, msg
            else:
                err = proc.stderr.strip() or proc.stdout.strip()
                return False, f"Failed to register Windows scheduled task: {err}"
        except OSError as exc:
            return False, f"schtasks execution failed: {exc}"

    # macOS and Linux: use crontab
    cron_entry = f"{minute} {hour} * * * {cmd} # DailyBriefMorning"
    try:
        # Read existing crontab
        read_proc = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=False)
        existing_lines = read_proc.stdout.splitlines() if read_proc.returncode == 0 else []

        # Filter out existing DailyBriefMorning lines
        filtered = [line for line in existing_lines if "# DailyBriefMorning" not in line and line.strip()]
        filtered.append(cron_entry)
        new_crontab = "\n".join(filtered) + "\n"

        write_proc = subprocess.run(
            ["crontab", "-"],
            input=new_crontab,
            capture_output=True,
            text=True,
            check=False,
        )
        if write_proc.returncode == 0:
            msg = (
                f"Otomatik sabah brifingi her gün saat {formatted_time} için zamanlandı (crontab)."
                if lang.lower() == "tr"
                else f"Autonomous morning briefing scheduled daily at {formatted_time} (crontab)."
            )
            return True, msg
        else:
            return False, f"Failed to update crontab: {write_proc.stderr.strip()}"
    except OSError as exc:
        return False, f"Crontab command failed: {exc}"


def unschedule_daily_task(lang: str = "en") -> tuple[bool, str]:
    if sys.platform == "win32":
        task_name = "DailyBriefMorning"
        try:
            proc = subprocess.run(
                ["schtasks", "/delete", "/tn", task_name, "/f"],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                msg = (
                    "Zamanlanmış görev başarıyla kaldırıldı."
                    if lang.lower() == "tr"
                    else "Scheduled morning briefing task removed successfully."
                )
                return True, msg
            else:
                err = proc.stderr.strip() or proc.stdout.strip()
                return False, f"Could not remove scheduled task: {err}"
        except OSError as exc:
            return False, f"schtasks delete failed: {exc}"

    # macOS / Linux
    try:
        read_proc = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=False)
        if read_proc.returncode != 0:
            msg = "Zamanlanmış görev bulunamadı." if lang.lower() == "tr" else "No scheduled task found in crontab."
            return True, msg

        existing_lines = read_proc.stdout.splitlines()
        filtered = [line for line in existing_lines if "# DailyBriefMorning" not in line]
        if len(filtered) == len(existing_lines):
            msg = "Zamanlanmış görev bulunamadı." if lang.lower() == "tr" else "No scheduled DailyBrief task found."
            return True, msg

        new_crontab = "\n".join(filtered) + ("\n" if filtered else "")
        write_proc = subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True, check=False)
        if write_proc.returncode == 0:
            msg = "Zamanlanmış görev crontab'dan kaldırıldı." if lang.lower() == "tr" else "Scheduled task removed from crontab."
            return True, msg
        return False, f"Failed to update crontab: {write_proc.stderr.strip()}"
    except OSError as exc:
        return False, f"Crontab failed: {exc}"


def send_desktop_notification(title: str, message: str) -> bool:
    try:
        if sys.platform == "win32":
            # PowerShell balloon tooltip or notification
            ps_script = (
                f"[reflection.assembly]::loadwithpartialname('System.Windows.Forms') | Out-Null; "
                f"$notify = New-Object System.Windows.Forms.NotifyIcon; "
                f"$notify.Icon = [System.Drawing.SystemIcons]::Information; "
                f"$notify.Visible = $True; "
                f"$notify.ShowBalloonTip(10000, '{title}', '{message}', [System.Windows.Forms.ToolTipIcon]::Info); "
                f"Start-Sleep -Milliseconds 500; "
                f"$notify.Dispose();"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                check=False,
                timeout=5,
            )
            return True
        elif sys.platform == "darwin":
            osa_script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", osa_script], capture_output=True, check=False, timeout=5)
            return True
        elif sys.platform.startswith("linux"):
            if shutil.which("notify-send"):
                subprocess.run(["notify-send", title, message], capture_output=True, check=False, timeout=5)
                return True
    except (subprocess.SubprocessError, OSError):
        pass
    return False


def run_background_briefing(
    source: Path,
    lang: str = "en",
    provider: str | None = None,
    model: str | None = None,
    git_repo: tuple[Path, ...] | None = None,
) -> bool:
    """Runs a silent, non-interactive briefing, pre-warms cache and sends desktop notification."""
    today = date.today().strftime("%Y-%m-%d")

    from dailybrief.cache import (
        CacheEntry,
        compute_git_hash,
        compute_notes_hash,
        compute_state_hash,
        get_cached_brief,
        save_cached_brief,
    )
    from dailybrief.git_context import collect_git_context
    from dailybrief.memory import save_history_entry
    from dailybrief.reader import read_notes
    from dailybrief.summarizer import generate_brief

    config = load_config()
    active_provider_name = provider or config.provider or "anthropic"
    active_model = model or config.model

    repos: list[Path | str] = []
    if git_repo:
        repos.extend(git_repo)
    if config.watched_repos:
        repos.extend(config.watched_repos)

    git_context = collect_git_context(repos if repos else None)

    try:
        notes = read_notes(source)
    except Exception:
        return False

    notes_hash = compute_notes_hash(notes)
    git_hash = compute_git_hash(git_context)
    state_hash = compute_state_hash(
        notes_hash=notes_hash,
        git_hash=git_hash,
        provider=active_provider_name,
        model=active_model or "default",
        lang=lang,
        date_str=today,
    )

    cached = get_cached_brief(state_hash, today)
    if cached is not None:
        brief = cached.brief
    else:
        api_key = resolve_api_key(active_provider_name, config)
        if not api_key and active_provider_name != "ollama":
            return False

        llm_provider = get_provider(active_provider_name, api_key=api_key)
        brief = generate_brief(
            notes=notes,
            lang=lang,
            provider=llm_provider,
            model=active_model,
            git_context=git_context,
        )

        entry = CacheEntry(
            state_hash=state_hash,
            date_str=today,
            brief=brief,
            notes_count=len(notes),
            created_at=0.0,
            provider=active_provider_name,
            model=active_model or "",
            lang=lang,
        )
        save_cached_brief(entry)

    save_history_entry(brief=brief, date_str=today, lang=lang, notes_count=len(notes))

    # Send desktop notification
    title = "DailyBrief ⚡"
    if lang.lower() == "tr":
        body = "Günün brifingi hazır! Terminalden 'dailybrief' çalıştırarak görüntüleyin."
    else:
        body = "Your daily briefing is ready! Run 'dailybrief' in your terminal to view."

    send_desktop_notification(title, body)
    return True
