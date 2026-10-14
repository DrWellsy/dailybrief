from __future__ import annotations

SUPPORTED_LANGS = ("en", "tr")
DEFAULT_LANG = "en"

MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "date_label": "Date",
        "header_title": "DailyBrief",
        "panel_title": "Daily Brief",
        "no_notes": "No notes found in source directory.",
        "no_notes_title": "Daily Brief",
        "compiled_from": "Compiled from {count} file(s)",
        "source_help": "Directory containing markdown and text notes.",
        "lang_help": "Language for interface and briefing (en/tr).",
        "cli_doc": "Generate a short daily briefing from notes in a folder.",
        "api_key_prompt": "Anthropic API key",
        "api_key_empty": "API key cannot be empty.",
        "api_key_read_error": "Could not read API configuration: {path} ({error})",
        "api_key_write_error": "Could not save API configuration: {path} ({error})",
        "api_key_missing_noninteractive": (
            "ANTHROPIC_API_KEY environment variable not found and terminal is non-interactive.\n"
            "Set it in PowerShell: $env:ANTHROPIC_API_KEY='your_api_key'\n"
            "or bash/zsh: export ANTHROPIC_API_KEY='your_api_key'"
        ),
        "api_key_missing_error": (
            "ANTHROPIC_API_KEY is not set. Please configure your API key first:\n"
            "PowerShell: $env:ANTHROPIC_API_KEY='your_api_key'\n"
            "bash/zsh: export ANTHROPIC_API_KEY='your_api_key'"
        ),
        "no_notes_for_summary": "No notes provided to generate brief.",
        "rate_limit_error": "Anthropic API rate limit reached. Please wait a moment and retry.",
        "connection_error": "Anthropic API connection error. Check your network connection.",
        "api_error": "Anthropic API error: {error}",
        "empty_brief_error": "Anthropic API returned an empty briefing.",
    },
    "tr": {
        "date_label": "Tarih",
        "header_title": "DailyBrief",
        "panel_title": "Günlük Brifing",
        "no_notes": "Kaynak klasörde not bulunamadı.",
        "no_notes_title": "Brifing",
        "compiled_from": "{count} dosyadan derlendi",
        "source_help": "Notların okunacağı klasör yolu.",
        "lang_help": "Arayüz ve üretilen brifing dili (en/tr).",
        "cli_doc": "Belirtilen klasördeki notlardan kısa bir günlük brifing üretir.",
        "api_key_prompt": "Anthropic API anahtarınız",
        "api_key_empty": "API anahtarı boş olamaz.",
        "api_key_read_error": "API ayarı okunamadı: {path} ({error})",
        "api_key_write_error": "API ayarı kaydedilemedi: {path} ({error})",
        "api_key_missing_noninteractive": (
            "ANTHROPIC_API_KEY bulunamadı ve terminal etkileşimli değil.\n"
            "PowerShell'de ayarlayın: $env:ANTHROPIC_API_KEY='your_api_key'\n"
            "veya bash/zsh: export ANTHROPIC_API_KEY='your_api_key'"
        ),
        "api_key_missing_error": (
            "ANTHROPIC_API_KEY bulunamadı. Önce API anahtarını ayarlayın:\n"
            "PowerShell: $env:ANTHROPIC_API_KEY='your_api_key'\n"
            "cmd.exe: set ANTHROPIC_API_KEY=your_api_key"
        ),
        "no_notes_for_summary": "Özet üretmek için not bulunamadı.",
        "rate_limit_error": "Anthropic API rate limit hatası. Biraz bekleyip tekrar deneyin.",
        "connection_error": "Anthropic API bağlantı hatası. İnternet bağlantınızı ve ağ erişiminizi kontrol edin.",
        "api_error": "Anthropic API hatası: {error}",
        "empty_brief_error": "Anthropic API boş bir özet döndü.",
    },
}

SYSTEM_PROMPTS: dict[str, str] = {
    "en": (
        "You are an executive personal assistant turning raw notes into a crisp, high-signal daily briefing.\n"
        "Input notes may be in Turkish, English, or a mix of both. Comprehend everything accurately and produce the briefing strictly in English.\n"
        "Output structure must contain exactly two sections:\n"
        "1) Key Priorities for Today (3-5 actionable bullet points)\n"
        "2) Things Not to Forget / Follow-ups (critical reminders, meetings, deadlines)\n"
        "Keep points concise, punchy, actionable, and non-redundant. Do not include introductory or closing remarks."
    ),
    "tr": (
        "Sen bir yönetici asistanı olarak dağınık notları net, yüksek odaklı bir günlük brifinge dönüştürüyorsun.\n"
        "Girdi notları Türkçe ve İngilizce karışık olabilir; her iki dili de anlayıp tek ve tutarlı bir brifingde birleştir.\n"
        "Çıktıyı sadece Türkçe ver. Çıktı şu iki bölümden oluşsun:\n"
        "1) Bugün Öncelikli 3-5 Madde\n"
        "2) Unutulmaması Gerekenler\n"
        "Kısa, net, uygulanabilir ve tekrar etmeyen maddeler yaz. Giriş veya kapanış nezaket cümleleri ekleme."
    ),
}


def get_message(lang: str, key: str, **kwargs: object) -> str:
    lang_normalized = lang.lower() if lang else DEFAULT_LANG
    table = MESSAGES.get(lang_normalized, MESSAGES[DEFAULT_LANG])
    template = table.get(key, MESSAGES[DEFAULT_LANG].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template


def get_system_prompt(lang: str) -> str:
    lang_normalized = lang.lower() if lang else DEFAULT_LANG
    return SYSTEM_PROMPTS.get(lang_normalized, SYSTEM_PROMPTS[DEFAULT_LANG])
