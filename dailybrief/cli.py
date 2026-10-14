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

from dailybrief.i18n import DEFAULT_LANG, SUPPORTED_LANGS, get_message
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
    help="Kaynagin alinacagi klasor yolu / Directory containing notes.",
)
@click.option(
    "--lang",
    "-l",
    type=click.Choice(list(SUPPORTED_LANGS), case_sensitive=False),
    default=DEFAULT_LANG,
    show_default=True,
    help="Arayuz ve brifing dili / Interface & briefing language (en/tr).",
)
def main(source: Path, lang: str) -> None:
    """Verilen klasordeki notlardan kisa bir gunluk brifing uretir / Generate daily brief from notes."""
    lang = lang.lower()
    today = date.today().strftime("%Y-%m-%d")
    date_label = get_message(lang, "date_label")

    header_text = Text()
    header_text.append("DailyBrief\n", style="bold cyan")
    header_text.append(f"{date_label}: {today}", style="dim")
    console.print(Panel(Align.center(header_text), border_style="cyan"))

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

    try:
        _ensure_api_key(lang=lang)
        brief = generate_brief(notes, lang=lang)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

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


if __name__ == "__main__":
    main()
