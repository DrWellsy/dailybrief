from __future__ import annotations

import os
from importlib import import_module
from types import ModuleType

from dailybrief.git_context import GitContext
from dailybrief.i18n import DEFAULT_LANG, get_message, get_system_prompt
from dailybrief.memory import HistoryEntry, format_history_for_prompt
from dailybrief.reader import Note


def _load_anthropic() -> ModuleType:
    try:
        return import_module("anthropic")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Anthropic SDK kurulu degil. Kurmak icin su komutu calistirin: pip install anthropic"
        ) from exc


def generate_brief(
    notes: list[Note],
    lang: str = DEFAULT_LANG,
    git_context: GitContext | None = None,
    history: list[HistoryEntry] | None = None,
) -> str:
    if not notes:
        raise RuntimeError(get_message(lang, "no_notes_for_summary"))

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(get_message(lang, "api_key_missing_error"))

    payload_sections: list[str] = []

    if history:
        history_text = format_history_for_prompt(history, lang=lang)
        if history_text:
            header = "ÖNCEKİ GÜNÜN HAFIZASI / PREVIOUS BRIEFING MEMORY:"
            payload_sections.append(f"{header}\n{history_text}")

    if git_context:
        git_text = git_context.format_for_prompt(lang=lang)
        if git_text:
            header = "GİT GELİŞTİRİCİ DURUMU / GIT REPO CONTEXT:"
            payload_sections.append(f"{header}\n{git_text}")

    notes_payload = "\n\n".join(
        [f"Dosya / File: {note.name}\nIcerik / Content:\n{note.content}" for note in notes]
    )
    payload_sections.append(f"GÜNCEL NOTLAR / TODAY'S NOTES:\n{notes_payload}")

    full_payload = "\n\n--------------------\n\n".join(payload_sections)

    anthropic = _load_anthropic()
    client = anthropic.Anthropic(api_key=api_key)

    user_instructions = {
        "en": "Analyze the following developer notes, git context, and previous memory to generate the requested two-section daily briefing:\n\n",
        "tr": "Aşağıdaki notları, git durumunu ve geçmiş brifing hafızasını analiz ederek istenen iki bölümlü kısa brifingi üret:\n\n",
    }
    user_prompt_prefix = user_instructions.get(lang.lower(), user_instructions[DEFAULT_LANG])

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=700,
            system=get_system_prompt(lang),
            messages=[
                {
                    "role": "user",
                    "content": f"{user_prompt_prefix}{full_payload}",
                }
            ],
        )
    except anthropic.RateLimitError as exc:
        raise RuntimeError(get_message(lang, "rate_limit_error")) from exc
    except anthropic.APIConnectionError as exc:
        raise RuntimeError(get_message(lang, "connection_error")) from exc
    except anthropic.APIError as exc:
        raise RuntimeError(get_message(lang, "api_error", error=str(exc))) from exc

    text_parts = [block.text for block in response.content if hasattr(block, "text")]
    brief = "\n".join(text_parts).strip()

    if not brief:
        raise RuntimeError(get_message(lang, "empty_brief_error"))

    return brief