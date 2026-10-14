from __future__ import annotations

import os
from importlib import import_module
from types import ModuleType

from dailybrief.i18n import DEFAULT_LANG, get_message, get_system_prompt
from dailybrief.reader import Note


def _load_anthropic() -> ModuleType:
    try:
        return import_module("anthropic")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Anthropic SDK kurulu degil. Kurmak icin su komutu calistirin: pip install anthropic"
        ) from exc


def generate_brief(notes: list[Note], lang: str = DEFAULT_LANG) -> str:
    if not notes:
        raise RuntimeError(get_message(lang, "no_notes_for_summary"))

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(get_message(lang, "api_key_missing_error"))

    notes_payload = "\n\n".join(
        [f"Dosya / File: {note.name}\nIcerik / Content:\n{note.content}" for note in notes]
    )

    anthropic = _load_anthropic()
    client = anthropic.Anthropic(api_key=api_key)

    user_instructions = {
        "en": "Analyze the following notes and generate the requested two-section daily briefing:\n\n",
        "tr": "Asagidaki notlari analiz et ve istenen iki bolumlu kisa brifingi uret:\n\n",
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
                    "content": f"{user_prompt_prefix}{notes_payload}",
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