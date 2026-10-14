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
        "no_git_help": "Disable scanning git activity and branch status.",
        "no_history_help": "Disable loading previous days' briefings for task follow-up.",
        "interactive_help": "Enable interactive menu after briefing (copy, export).",
        "cli_doc": "Your personal AI developer assistant. Turns daily notes and git context into an executive briefing.",
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
        "git_banner": "Git Context: branch '{branch}' | {commits} commit(s) last 48h | {uncommitted} uncommitted",
        "history_banner": "Memory: Carried context from previous briefing ({date})",
        "interactive_hint": "[c] Copy standup to clipboard  •  [s] Save to markdown  •  [Enter] Exit",
        "clipboard_success": "Copied standup summary to clipboard!",
        "clipboard_failure": "Could not access system clipboard.",
        "export_success": "Saved briefing to: {path}",
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
        "no_git_help": "Git aktiviteleri ve branch durumunu taramayı devre dışı bırakır.",
        "no_history_help": "Önceki günlerin brifing hafızasını devre dışı bırakır.",
        "interactive_help": "Brifing sonrasında etkileşimli menüyü (kopyala, dışa aktar) açar.",
        "cli_doc": "Kişisel yapay zeka geliştirici asistanınız. Notları ve Git geçmişini özet brifinge dönüştürür.",
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
        "git_banner": "Git Durumu: '{branch}' dalı | Son 48 saatte {commits} commit | {uncommitted} değişiklik",
        "history_banner": "Hafıza: Önceki brifingden ({date}) görev devamlılığı sağlandı",
        "interactive_hint": "[c] Standup metnini panoya kopyala  •  [s] Markdown olarak kaydet  •  [Enter] Çık",
        "clipboard_success": "Standup metni panoya kopyalandı!",
        "clipboard_failure": "Sistem panosuna erişilemedi.",
        "export_success": "Brifing kaydedildi: {path}",
    },
}

SYSTEM_PROMPTS: dict[str, str] = {
    "en": (
        "You are an executive developer assistant and personal Chief of Staff turning raw notes and engineering context into a crisp, high-signal daily briefing.\n"
        "Input notes may be in Turkish, English, or mixed. Always produce the briefing strictly in English.\n"
        "If Git context or previous day's briefing history is provided, connect the dots:\n"
        "- If a task was planned yesterday and is still unfinished or mentioned in today's notes, highlight it as carried over.\n"
        "- If there are uncommitted changes or recent commits, reflect their next step in priorities.\n"
        "Output structure must contain exactly two sections:\n"
        "1) Key Priorities for Today (3-5 actionable bullet points)\n"
        "2) Things Not to Forget / Follow-ups (deadlines, meetings, follow-ups, carry-overs)\n"
        "Keep points concise, punchy, actionable, and non-redundant. Do not include introductory or closing remarks."
    ),
    "tr": (
        "Sen bir yönetici geliştirici asistanı ve kişisel danışmansın. Dağınık notları, Git durumunu ve dünden kalan görevleri net bir günlük brifinge dönüştürüyorsun.\n"
        "Girdi notları Türkçe ve İngilizce karışık olabilir; her iki dili de anlayıp brifingi sadece Türkçe ver.\n"
        "Eğer Git durumu veya dünün brifing hafızası verildiyse:\n"
        "- Dünden yarım kalan veya devam eden bir iş varsa bunu 'Dünden Devam Edenler' bağlamında vurgula.\n"
        "- Git'teki yarım kalan değişiklikler veya son commit'lerin gerektirdiği adımları önceliklere yansıt.\n"
        "Çıktı şu iki bölümden oluşsun:\n"
        "1) Bugün Öncelikli 3-5 Madde\n"
        "2) Unutulmaması Gerekenler (Toplantılar, takipler, dünden devredenler)\n"
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
