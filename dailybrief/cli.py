from __future__ import annotations

from datetime import date
import os
from pathlib import Path
import sys

import click
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from dailybrief.actions import (
    append_task_breakdown,
    checkout_branch,
    copy_to_clipboard,
    export_brief,
    format_standup_text,
    generate_branch_name,
)
from dailybrief.blockers import (
    detect_blockers,
    extract_priorities_from_brief,
    render_blocker_panel,
)
from dailybrief.config import (
    AppConfig,
    DEFAULT_CONFIG_PATH,
    ENV_KEY_NAMES,
    load_config,
    resolve_api_key,
    save_config,
    set_api_key_for_provider,
)
from dailybrief.eod import (
    format_eod_standup,
    reconcile_eod,
    render_eod_panel,
    save_eod_summary,
)
from dailybrief.git_context import collect_git_context
from dailybrief.git_radar import inspect_git_radar, render_radar_panel
from dailybrief.i18n import DEFAULT_LANG, SUPPORTED_LANGS, get_message
from dailybrief.mcp_server import run_mcp_server
from dailybrief.memory import load_recent_history, save_history_entry
from dailybrief.providers import get_provider
from dailybrief.reader import read_notes
from dailybrief.summarizer import break_down_task, generate_brief, refine_brief
from dailybrief.voice import (
    generate_voice_script,
    play_audio_file,
    synthesize_brief_audio,
)

# Reconfigure Windows stdout/stderr to utf-8 if needed to safely render rich emojis
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console()
CONFIG_PATH = DEFAULT_CONFIG_PATH


def _saved_api_key() -> str | None:
    cfg = load_config()
    return cfg.anthropic_api_key or cfg.api_key


def _ensure_api_key(
    provider_name: str = "anthropic",
    config: AppConfig | None = None,
    lang: str = DEFAULT_LANG,
) -> str | None:
    active_config = config or load_config()
    key = resolve_api_key(provider_name, active_config)
    if key is not None:
        return key

    if not sys.stdin.isatty():
        env_vars = ENV_KEY_NAMES.get(provider_name, ("API_KEY",))
        primary_var = env_vars[0] if env_vars else "API_KEY"
        raise RuntimeError(
            get_message(lang, "api_key_missing_noninteractive", env_var=primary_var)
        )

    prompt_label = get_message(lang, "api_key_prompt", provider=provider_name.capitalize())
    entered_key = click.prompt(prompt_label, hide_input=True).strip()
    if not entered_key:
        raise RuntimeError(get_message(lang, "api_key_empty"))

    set_api_key_for_provider(provider_name, entered_key, active_config)
    try:
        save_config(active_config)
    except OSError as exc:
        raise RuntimeError(
            get_message(lang, "api_key_write_error", path=CONFIG_PATH, error=exc)
        ) from exc

    # Set in env as well
    env_vars = ENV_KEY_NAMES.get(provider_name, ())
    for ev in env_vars:
        os.environ[ev] = entered_key

    return entered_key


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--source",
    "-s",
    default="./notes",
    show_default=True,
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Notlarin okunacagi klasor / Directory containing notes.",
)
@click.option(
    "--lang",
    "-l",
    type=click.Choice(list(SUPPORTED_LANGS), case_sensitive=False),
    default=DEFAULT_LANG,
    show_default=True,
    help="Arayuz ve brifing dili / Interface & briefing language (en/tr).",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["anthropic", "openai", "gemini", "ollama"], case_sensitive=False),
    default=None,
    help="Yapay zeka saglayicisi / LLM provider (anthropic, openai, gemini, ollama).",
)
@click.option(
    "--model",
    "-m",
    default=None,
    help="Model adi / Model override (e.g. claude-sonnet-4-6, gpt-4o, llama3.2).",
)
@click.option(
    "--git-repo",
    "-g",
    multiple=True,
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Izlenecek Git deposu / Git repository to watch (can be repeated).",
)
@click.option(
    "--no-git",
    is_flag=True,
    default=False,
    help="Git durumu ve commit taramasini devre disi birakir / Disable git scanning.",
)
@click.option(
    "--no-history",
    is_flag=True,
    default=False,
    help="Onceki gunlerin brifing hafizasini devre disi birakir / Disable memory.",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    default=False,
    help="Brifing sonrasi etkilesimli aksiyon menusu / Interactive action menu after briefing.",
)
@click.option(
    "--eod",
    is_flag=True,
    default=False,
    help="Gun sonu mutabakati / End-of-Day reconciliation mode.",
)
@click.option(
    "--voice",
    is_flag=True,
    default=False,
    help="Sesli brifing uret ve oynat / Executive spoken audio briefing.",
)
@click.option(
    "--mcp",
    is_flag=True,
    default=False,
    help="MCP (Model Context Protocol) stdio sunucu modu / Run as MCP server.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Anlik onbellegi atlar ve taze brifing uretir / Bypass instant cache.",
)
@click.option(
    "--schedule",
    default=None,
    help="Gunluk otonom sabah brifingi saati (SS:DD) / Schedule autonomous daily briefing (HH:MM).",
)
@click.option(
    "--unschedule",
    is_flag=True,
    default=False,
    help="Zamanlanmis otonom gorevi kaldirir / Remove scheduled task.",
)
@click.option(
    "--background",
    is_flag=True,
    default=False,
    help="Sessiz arka plan modu ve masaustu bildirimi / Run in background mode with desktop notification.",
)
@click.option(
    "--doctor",
    is_flag=True,
    default=False,
    help="Sistem tanilamasi / Run system self-diagnostics.",
)
def main(
    source: Path,
    lang: str,
    provider: str | None,
    model: str | None,
    git_repo: tuple[Path, ...],
    no_git: bool,
    no_history: bool,
    interactive: bool,
    eod: bool,
    voice: bool,
    mcp: bool,
    force: bool = False,
    schedule: str | None = None,
    unschedule: bool = False,
    background: bool = False,
    doctor: bool = False,
) -> None:
    """Kisisel yapay zeka asistaniniz / Your personal executive developer assistant."""
    lang = lang.lower()

    # 1. MCP Mode: run stdio server immediately
    if mcp:
        run_mcp_server()
        return

    # 2. Doctor Diagnostics Mode
    if doctor:
        from dailybrief.doctor import render_doctor_table, run_doctor

        checks = run_doctor(lang=lang, notes_dir=source)
        console.print(render_doctor_table(checks, lang=lang))
        return

    # 3. Autonomous Scheduler Operations
    if schedule:
        from dailybrief.scheduler import schedule_daily_task

        ok, msg = schedule_daily_task(schedule, lang=lang)
        if ok:
            console.print(Text("✔ " + msg, style="bold green"))
        else:
            console.print(Text("✘ " + msg, style="bold red"))
        return

    if unschedule:
        from dailybrief.scheduler import unschedule_daily_task

        ok, msg = unschedule_daily_task(lang=lang)
        if ok:
            console.print(Text("✔ " + msg, style="bold green"))
        else:
            console.print(Text("✘ " + msg, style="bold red"))
        return

    # 4. Background Autonomous Execution
    if background:
        from dailybrief.scheduler import run_background_briefing

        run_background_briefing(
            source=source,
            lang=lang,
            provider=provider,
            model=model,
            git_repo=git_repo,
        )
        return

    today = date.today().strftime("%Y-%m-%d")
    date_label = get_message(lang, "date_label")

    # Load configuration
    config = load_config()

    # Determine Git Repositories
    repos_to_check: list[Path | str] = []
    if git_repo:
        repos_to_check.extend(git_repo)
    if config.watched_repos:
        repos_to_check.extend(config.watched_repos)

    git_context = None
    if not no_git:
        git_context = collect_git_context(repos_to_check if repos_to_check else None)

    # ----------------------------------------------------
    # End-of-Day (EOD) Reconciliation Mode
    # ----------------------------------------------------
    if eod:
        today_history = load_recent_history(days=2)
        morning_brief = None
        for h in today_history:
            if h.date == today:
                morning_brief = h.brief
                break
        if not morning_brief and today_history:
            morning_brief = today_history[0].brief

        if not morning_brief:
            console.print(Text("⚠️ " + get_message(lang, "eod_no_brief"), style="bold yellow"))
            return

        note_texts: list[str] = []
        try:
            notes = read_notes(source)
            note_texts = [n.content for n in notes]
        except Exception:
            pass

        git_commits = git_context.recent_commits if git_context else []
        git_mod_files = git_context.modified_files if git_context else []

        eod_summary = reconcile_eod(
            morning_brief=morning_brief,
            date_str=today,
            git_commits=git_commits,
            git_modified_files=git_mod_files,
            note_contents=note_texts,
            lang=lang,
        )

        console.print(render_eod_panel(eod_summary, lang=lang))
        saved_path = save_eod_summary(eod_summary)
        console.print(Text(get_message(lang, "eod_saved", path=saved_path.name), style="dim"))

        if sys.stdin.isatty():
            console.print()
            prompt_hint = "[c] Standup metnini panoya kopyala  •  [Enter] Çık" if lang == "tr" else "[c] Copy EOD Standup to clipboard  •  [Enter] Exit"
            console.print(Text(prompt_hint, style="bold cyan"))
            c_input = click.prompt(">>", default="", show_default=False).strip().lower()
            if c_input == "c":
                eod_text = format_eod_standup(eod_summary, lang=lang)
                if copy_to_clipboard(eod_text):
                    console.print(Text("OK: " + get_message(lang, "clipboard_success"), style="green"))
                else:
                    console.print(Text("WARN: " + get_message(lang, "clipboard_failure"), style="yellow"))
        return

    # ----------------------------------------------------
    # Morning / Standard Briefing Mode
    # ----------------------------------------------------
    active_provider_name = (provider or config.provider or "anthropic").lower()
    active_model = model or config.model

    # Header Panel
    header_text = Text()
    header_text.append("DailyBrief\n", style="bold cyan")
    provider_info = f"Provider: {active_provider_name}"
    if active_model:
        provider_info += f" ({active_model})"
    header_text.append(f"{date_label}: {today}  •  {provider_info}", style="dim")
    console.print(Panel(Align.center(header_text), border_style="cyan"))

    # 1. Multi-Repo Git Context Sensing
    if git_context:
        banner = git_context.format_banner(lang)
        console.print(Text(f"[Git] {banner}", style="dim cyan"))

    # 2. History Memory Sensing
    history_entries = None
    if not no_history:
        history_entries = load_recent_history(days=5, exclude_date=today)
        if history_entries:
            banner = get_message(lang, "history_banner", date=history_entries[0].date)
            console.print(Text(f"[Memory] {banner}", style="dim yellow"))

    # 3. Read Notes
    try:
        notes = read_notes(source)
    except ValueError:
        no_notes_msg = get_message(lang, "no_notes")
        no_notes_title = get_message(lang, "no_notes_title")
        compiled_from_0 = get_message(lang, "compiled_from", count=0)
        console.print(
            Panel(
                no_notes_msg,
                title=no_notes_title,
                border_style="yellow",
            )
        )
        console.print(Text(compiled_from_0, style="dim"))
        return
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise click.ClickException(str(exc)) from exc

    # 4. Predictive Git Conflict & Upstream Radar
    if not no_git:
        radar_alerts = inspect_git_radar(
            repo_paths=repos_to_check if repos_to_check else None,
            local_modified_files=git_context.modified_files if git_context else None,
            note_contents=[n.content for n in notes],
            lang=lang,
        )
        if radar_alerts:
            radar_panel = render_radar_panel(radar_alerts, lang=lang)
            if radar_panel:
                console.print(radar_panel)

    # 5. Chronic Blocker / Carry-Over Detection
    if history_entries:
        git_commits = git_context.recent_commits if git_context else None
        git_mod_files = git_context.modified_files if git_context else None
        note_texts = [n.content for n in notes]
        blockers = detect_blockers(
            history_entries=history_entries,
            git_commits=git_commits,
            git_modified_files=git_mod_files,
            note_contents=note_texts,
            lang=lang,
        )
        if blockers:
            blocker_panel = render_blocker_panel(blockers, lang=lang)
            if blocker_panel:
                console.print(blocker_panel)

    # 6. Smart Content-Hash Caching & Token Optimization
    from dailybrief.cache import (
        CacheEntry,
        compute_git_hash,
        compute_notes_hash,
        compute_state_hash,
        get_cached_brief,
        render_cache_badge,
        save_cached_brief,
    )
    import time

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

    brief: str | None = None
    loaded_from_cache = False

    if not force:
        cached_entry = get_cached_brief(state_hash, today)
        if cached_entry is not None:
            brief = cached_entry.brief
            loaded_from_cache = True

    if brief is None:
        # Resolve API Key & Provider
        try:
            api_key = _ensure_api_key(
                provider_name=active_provider_name,
                config=config,
                lang=lang,
            )
            llm_provider = get_provider(
                provider_name=active_provider_name,
                api_key=api_key,
                ollama_host=config.ollama_host,
            )
        except (RuntimeError, ValueError) as exc:
            raise click.ClickException(str(exc)) from exc

        # 7. Generate Brief with LLM
        try:
            brief = generate_brief(
                notes,
                lang=lang,
                git_context=git_context,
                history=history_entries,
                provider=llm_provider,
                model=active_model,
            )
        except RuntimeError as exc:
            raise click.ClickException(str(exc)) from exc

        # Save to Instant Content-Hash Cache
        try:
            save_cached_brief(
                CacheEntry(
                    state_hash=state_hash,
                    date_str=today,
                    brief=brief,
                    notes_count=len(notes),
                    created_at=time.time(),
                    provider=active_provider_name,
                    model=active_model or "",
                    lang=lang,
                )
            )
        except Exception:
            pass

    # 8. Output Panel
    panel_title = get_message(lang, "panel_title")
    console.print(
        Panel(
            brief,
            title=panel_title,
            border_style="green",
            padding=(1, 2),
        )
    )
    compiled_from_n = get_message(lang, "compiled_from", count=len(notes))
    console.print(Text(compiled_from_n, style="dim"))

    if loaded_from_cache:
        console.print(render_cache_badge(lang))

    # 9. Save to Persistent Memory
    try:
        save_history_entry(brief=brief, date_str=today, lang=lang, notes_count=len(notes))
    except OSError:
        pass

    # 10. Voice Audio Briefing (if requested via --voice)
    if voice:
        voice_script = generate_voice_script(brief, date_str=today, lang=lang)
        audio_path, used_synth = synthesize_brief_audio(
            voice_script,
            provider=config.voice_provider,
            openai_key=config.openai_api_key,
            voice=config.voice_name,
        )
        if audio_path and audio_path.exists():
            play_audio_file(audio_path, console=console)
        else:
            console.print(Text("ℹ️ " + get_message(lang, "voice_unavailable"), style="dim"))

    # 11. True Agentic Interactive Loop
    if interactive and sys.stdin.isatty():
        hint = get_message(lang, "interactive_hint")
        while True:
            console.print()
            console.print(Text(hint, style="bold cyan"))
            choice = click.prompt(">>", default="", show_default=False).strip().lower()

            if not choice or choice in ("q", "quit", "exit"):
                break
            elif choice == "c":
                standup_text = format_standup_text(brief, date_str=today, lang=lang)
                if copy_to_clipboard(standup_text):
                    console.print(Text("OK: " + get_message(lang, "clipboard_success"), style="green"))
                else:
                    console.print(Text("WARN: " + get_message(lang, "clipboard_failure"), style="yellow"))
            elif choice == "s":
                export_path = export_brief(brief, date_str=today)
                console.print(Text("OK: " + get_message(lang, "export_success", path=export_path.name), style="green"))
            elif choice == "b":
                priorities = extract_priorities_from_brief(brief)
                if not priorities:
                    console.print(Text("WARN: " + get_message(lang, "no_tasks_to_break"), style="yellow"))
                    continue

                for idx, t in enumerate(priorities, start=1):
                    console.print(Text(f"  {idx}. {t}", style="dim"))

                p_prompt = get_message(lang, "break_down_prompt", max_num=len(priorities))
                selected = click.prompt(p_prompt, default="1").strip()
                if selected.isdigit() and 1 <= int(selected) <= len(priorities):
                    target_task = priorities[int(selected) - 1]
                else:
                    target_task = selected or priorities[0]

                console.print(Text(f"... Breaking down task with {active_provider_name} ...", style="dim cyan"))
                try:
                    breakdown = break_down_task(
                        target_task,
                        lang=lang,
                        provider=llm_provider,
                        model=active_model,
                    )
                    b_path = append_task_breakdown(
                        breakdown,
                        task_title=target_task,
                        date_str=today,
                        target_dir=source if source.is_dir() else Path.cwd(),
                    )
                    console.print(
                        Panel(
                            breakdown,
                            title=f"Checklist: {target_task[:50]}",
                            border_style="cyan",
                            padding=(1, 2),
                        )
                    )
                    console.print(Text("OK: " + get_message(lang, "break_down_success", path=b_path.name), style="green"))
                except RuntimeError as exc:
                    console.print(Text(f"ERROR: {exc}", style="red"))
            elif choice == "g":
                priorities = extract_priorities_from_brief(brief)
                task_for_branch = priorities[0] if priorities else "feature-work"
                proposed_branch = generate_branch_name(task_for_branch)

                target_repo_path = Path.cwd()
                repo_name = target_repo_path.name
                if git_context and git_context.repos:
                    if len(git_context.repos) > 1:
                        select_title = "Hedef Git deposunu seçin:" if lang == "tr" else "Select target Git repository:"
                        console.print(Text(select_title, style="dim cyan"))
                        for r_idx, r in enumerate(git_context.repos, start=1):
                            console.print(Text(f"  {r_idx}. {r.name} ({r.path})", style="dim"))
                        sel_str = click.prompt(">>", default="1").strip()
                        if sel_str.isdigit() and 1 <= int(sel_str) <= len(git_context.repos):
                            chosen_repo = git_context.repos[int(sel_str) - 1]
                        else:
                            chosen_repo = git_context.repos[0]
                        target_repo_path = chosen_repo.path
                        repo_name = chosen_repo.name
                    else:
                        target_repo_path = git_context.repos[0].path
                        repo_name = git_context.repos[0].name

                confirm_prompt = get_message(
                    lang, "branch_confirm_prompt", branch=proposed_branch, repo=repo_name
                )
                confirm = click.prompt(confirm_prompt, default="y").strip().lower()
                if confirm in ("y", "yes", "e", "evet", ""):
                    success, msg = checkout_branch(proposed_branch, repo_path=target_repo_path)
                    if success:
                        console.print(Text("OK: " + get_message(lang, "branch_success", branch=proposed_branch, repo=repo_name), style="green"))
                    else:
                        console.print(Text("ERROR: " + get_message(lang, "branch_failure", error=msg), style="red"))
            elif choice == "r":
                refine_prompt_text = get_message(lang, "refine_prompt")
                instruction = click.prompt(refine_prompt_text).strip()
                if instruction:
                    console.print(Text(f"... Refining briefing with {active_provider_name} ...", style="dim cyan"))
                    try:
                        brief = refine_brief(
                            brief,
                            instruction=instruction,
                            lang=lang,
                            provider=llm_provider,
                            model=active_model,
                        )
                        console.print(
                            Panel(
                                brief,
                                title=get_message(lang, "panel_title") + " (Refined)",
                                border_style="green",
                                padding=(1, 2),
                            )
                        )
                        save_history_entry(brief=brief, date_str=today, lang=lang, notes_count=len(notes))
                        console.print(Text("OK: " + get_message(lang, "refine_success"), style="green"))
                    except RuntimeError as exc:
                        console.print(Text(f"ERROR: {exc}", style="red"))


if __name__ == "__main__":
    main()
