from __future__ import annotations

from datetime import date
import json
import os
from pathlib import Path
import re
import sys

import click
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from dailybrief.actions import copy_to_clipboard, export_brief, format_standup_text
from dailybrief.git_context import collect_git_context
from dailybrief.i18n import DEFAULT_LANG, SUPPORTED_LANGS, get_message
from dailybrief.memory import load_recent_history, save_history_entry
from dailybrief.reader import read_notes
from dailybrief.summarizer import generate_brief

console = Console()
CONFIG_PATH = Path.home() / ".dailybrief" / "config.toml"


def _saved_api_key() -> str | None:
    try:
        config = CONFIG_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise RuntimeError(f"API ayari okunamadi: {CONFIG_PATH} ({exc})") from exc

    match = re.search(r'^\s*api_key\s*=\s*["\'](.*?)["\']\s*$', config, re.MULTILINE)
    return match.group(1) if match else None


def _ensure_api_key(lang: str = DEFAULT_LANG) -> None:
    if os.getenv("ANTHROPIC_API_KEY"):
        return

    saved_key = _saved_api_key()
    if saved_key:
        os.environ["ANTHROPIC_API_KEY"] = saved_key
        return

    if not sys.stdin.isatty():
        raise RuntimeError(get_message(lang, "api_key_missing_noninteractive"))

    prompt_label = get_message(lang, "api_key_prompt")
    api_key = click.prompt(prompt_label, hide_input=True).strip()
    if not api_key:
        raise RuntimeError(get_message(lang, "api_key_empty"))

    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            f"api_key = {json.dumps(api_key)}\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise RuntimeError(get_message(lang, "api_key_write_error", path=CONFIG_PATH, error=exc)) from exc

    os.environ["ANTHROPIC_API_KEY"] = api_key


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
def main(
    source: Path,
    lang: str,
    no_git: bool,
    no_history: bool,
    interactive: bool,
) -> None:
    """Kisisel yapay zeka asistaniniz / Your personal executive developer assistant."""
    lang = lang.lower()
    today = date.today().strftime("%Y-%m-%d")
    date_label = get_message(lang, "date_label")

    # Header Panel
    header_text = Text()
    header_text.append("DailyBrief\n", style="bold cyan")
    header_text.append(f"{date_label}: {today}", style="dim")
    console.print(Panel(Align.center(header_text), border_style="cyan"))

    # 1. Git Context Sensing
    git_context = None
    if not no_git:
        git_context = collect_git_context()
        if git_context:
            banner = get_message(
                lang,
                "git_banner",
                branch=git_context.branch,
                commits=len(git_context.recent_commits),
                uncommitted=git_context.uncommitted_count,
            )
            console.print(Text(f"[Git] {banner}", style="dim cyan"))

    # 2. History Memory Sensing
    history_entries = None
    if not no_history:
        history_entries = load_recent_history(days=2, exclude_date=today)
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

    # 4. Generate Brief with Claude
    try:
        _ensure_api_key(lang=lang)
        brief = generate_brief(
            notes,
            lang=lang,
            git_context=git_context,
            history=history_entries,
        )
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    # 5. Output Panel
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

    # 6. Save to Persistent Memory
    try:
        save_history_entry(brief=brief, date_str=today, lang=lang, notes_count=len(notes))
    except OSError:
        pass

    # 7. Interactive Actions Menu
    if interactive and sys.stdin.isatty():
        hint = get_message(lang, "interactive_hint")
        console.print()
        console.print(Text(hint, style="bold cyan"))
        choice = click.prompt(">>", default="", show_default=False).strip().lower()

        if choice == "c":
            standup_text = format_standup_text(brief, date_str=today, lang=lang)
            if copy_to_clipboard(standup_text):
                console.print(Text("OK: " + get_message(lang, "clipboard_success"), style="green"))
            else:
                console.print(Text("WARN: " + get_message(lang, "clipboard_failure"), style="yellow"))
        elif choice == "s":
            export_path = export_brief(brief, date_str=today)
            console.print(Text("OK: " + get_message(lang, "export_success", path=export_path.name), style="green"))


if __name__ == "__main__":
    main()
