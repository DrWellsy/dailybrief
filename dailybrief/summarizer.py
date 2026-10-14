from __future__ import annotations

import os
from types import ModuleType

from dailybrief.git_context import GitContext
from dailybrief.i18n import DEFAULT_LANG, get_message, get_system_prompt
from dailybrief.memory import HistoryEntry, format_history_for_prompt
from dailybrief.providers import AnthropicProvider, LLMProvider, _load_anthropic as _providers_load_anthropic
from dailybrief.reader import Note


def _load_anthropic() -> ModuleType:
    return _providers_load_anthropic()


def generate_brief(
    notes: list[Note],
    lang: str = DEFAULT_LANG,
    git_context: GitContext | None = None,
    history: list[HistoryEntry] | None = None,
    provider: LLMProvider | None = None,
    model: str | None = None,
) -> str:
    if not notes:
        raise RuntimeError(get_message(lang, "no_notes_for_summary"))

    active_provider = provider or AnthropicProvider()

    # If anthropic is used and no API key is set, raise the localized error
    if active_provider.name == "anthropic" and not os.getenv("ANTHROPIC_API_KEY") and not getattr(active_provider, "api_key", None):
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

    user_instructions = {
        "en": "Analyze the following developer notes, git context, and previous memory to generate the requested two-section daily briefing:\n\n",
        "tr": "Aşağıdaki notları, git durumunu ve geçmiş brifing hafızasını analiz ederek istenen iki bölümlü kısa brifingi üret:\n\n",
    }
    user_prompt_prefix = user_instructions.get(lang.lower(), user_instructions[DEFAULT_LANG])
    user_prompt = f"{user_prompt_prefix}{full_payload}"
    system_prompt = get_system_prompt(lang)

    return active_provider.generate(system_prompt=system_prompt, user_prompt=user_prompt, model=model)


def break_down_task(
    task_text: str,
    lang: str = DEFAULT_LANG,
    provider: LLMProvider | None = None,
    model: str | None = None,
) -> str:
    active_provider = provider or AnthropicProvider()
    is_tr = lang.lower() == "tr"

    if is_tr:
        system_prompt = (
            "Sen kıdemli bir yazılım mimarısın. Verilen görevi 3 somut, teknik ve uygulanabilir "
            "alt adıma böl. Her adım için tahmini süre ve doğrulama kriteri belirt. "
            "Gereksiz nezaket cümleleri yazma, doğrudan Markdown kontrol listesi ver."
        )
        user_prompt = f"Görevi 3 somut adıma böl:\n\n{task_text}"
    else:
        system_prompt = (
            "You are a senior software architect. Break down the given task into 3 concrete, "
            "actionable technical implementation steps. Include time estimates and verification criteria. "
            "Do not include conversational filler; return clean Markdown checklist."
        )
        user_prompt = f"Break down this task into 3 actionable steps:\n\n{task_text}"

    return active_provider.generate(system_prompt=system_prompt, user_prompt=user_prompt, model=model)


def refine_brief(
    current_brief: str,
    instruction: str,
    lang: str = DEFAULT_LANG,
    provider: LLMProvider | None = None,
    model: str | None = None,
) -> str:
    active_provider = provider or AnthropicProvider()
    is_tr = lang.lower() == "tr"

    if is_tr:
        system_prompt = (
            "Sen bir yönetici asistanısın. Verilen brifingi kullanıcının düzeltme talimatına göre "
            "güncelle. İki bölümlü orijinal brifing formatını ('Bugün Öncelikli 3-5 Madde' ve "
            "'Unutulmaması Gerekenler') kesinlikle koru."
        )
        user_prompt = (
            f"Mevcut Brifing:\n{current_brief}\n\n"
            f"Düzeltme Talimatı:\n{instruction}\n\n"
            "Güncellenmiş brifingi üret:"
        )
    else:
        system_prompt = (
            "You are an executive developer assistant. Update the provided daily briefing based on the "
            "user's refinement instructions. Maintain the exact two-section format intact."
        )
        user_prompt = (
            f"Current Briefing:\n{current_brief}\n\n"
            f"Refinement Instruction:\n{instruction}\n\n"
            "Generate the updated briefing:"
        )

    return active_provider.generate(system_prompt=system_prompt, user_prompt=user_prompt, model=model)