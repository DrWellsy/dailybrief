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
        "provider_help": "LLM provider: anthropic, openai, gemini, ollama.",
        "model_help": "Model name override (e.g. claude-sonnet-4-6, gpt-4o, llama3.2).",
        "git_repo_help": "Git repository path to watch (can be repeated for multi-repo).",
        "no_git_help": "Disable scanning git activity and branch status.",
        "no_history_help": "Disable loading previous days' briefings for task follow-up.",
        "interactive_help": "Enable interactive agent actions after briefing.",
        "eod_help": "End-of-Day reconciliation mode: reconcile morning tasks against git commits and notes.",
        "voice_help": "Generate and play an executive spoken audio briefing.",
        "mcp_help": "Run as an MCP (Model Context Protocol) stdio server for Cursor, Windsurf, Claude Desktop.",
        "cli_doc": "Your personal AI executive developer assistant. Multi-LLM, local Ollama, git-aware with persistent memory.",
        "api_key_prompt": "{provider} API key",
        "api_key_empty": "API key cannot be empty.",
        "api_key_read_error": "Could not read API configuration: {path} ({error})",
        "api_key_write_error": "Could not save API configuration: {path} ({error})",
        "api_key_missing_noninteractive": (
            "{env_var} environment variable not found and terminal is non-interactive.\n"
            "Set it in PowerShell: $env:{env_var}='your_api_key'\n"
            "or bash/zsh: export {env_var}='your_api_key'"
        ),
        "api_key_missing_error": (
            "ANTHROPIC_API_KEY is not set. Please configure your API key first:\n"
            "PowerShell: $env:ANTHROPIC_API_KEY='your_api_key'\n"
            "bash/zsh: export ANTHROPIC_API_KEY='your_api_key'"
        ),
        "no_notes_for_summary": "No notes provided to generate brief.",
        "rate_limit_error": "API rate limit reached. Please wait a moment and retry.",
        "connection_error": "API connection error. Check your network connection.",
        "api_error": "API error: {error}",
        "empty_brief_error": "API returned an empty briefing.",
        "git_banner": "Git Context: {banner}",
        "history_banner": "Memory: Carried context from previous briefing ({date})",
        "interactive_hint": "[c] Copy Standup  •  [s] Save MD  •  [b] Break Down  •  [g] Branch  •  [r] Refine  •  [Enter] Exit",
        "clipboard_success": "Copied standup summary to clipboard!",
        "clipboard_failure": "Could not access system clipboard.",
        "export_success": "Saved briefing to: {path}",
        "break_down_prompt": "Enter priority number (1-{max_num}) to break down (or task text):",
        "break_down_success": "Task breakdown appended to: {path}",
        "no_tasks_to_break": "No priority tasks found to break down.",
        "branch_confirm_prompt": "Create & checkout branch '{branch}' in '{repo}'? [Y/n]:",
        "branch_success": "Switched to branch '{branch}' in '{repo}'!",
        "branch_failure": "Failed to checkout branch: {error}",
        "no_repo_for_branch": "No git repository found for branch checkout.",
        "refine_prompt": "Enter refinement instruction (e.g. 'Drop task 2, prioritize auth bug'):",
        "refine_success": "Briefing updated and persisted to memory!",
        "eod_no_brief": "No morning briefing found for today to reconcile. Run 'dailybrief' first to establish morning priorities.",
        "eod_saved": "End-of-day reconciliation saved to: {path}",
        "voice_unavailable": "Voice synthesis unavailable (no audio synthesizer or speech API configured).",
        "force_help": "Bypass instant cache and regenerate briefing with LLM.",
        "schedule_help": "Schedule autonomous daily morning briefing at specified time (HH:MM e.g. 08:45).",
        "unschedule_help": "Remove active autonomous morning briefing schedule.",
        "background_help": "Run silent background briefing, pre-warm cache, and send desktop notification.",
        "doctor_help": "Run system self-diagnostics for config, API keys, Git repos, and cache.",
        "redact_pii_help": "Mask email and IP addresses in notes in addition to credentials.",
        "no_todos_help": "Disable scanning codebase inline TODO/FIXME comments.",
        "weekly_help": "Generate weekly sprint retrospective and velocity scorecard.",
        "init_shell_help": "Generate shell auto-greeting hook for bash, zsh, powershell, or fish.",
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
        "provider_help": "Yapay zeka sağlayıcısı: anthropic, openai, gemini, ollama.",
        "model_help": "Model adı (ör. claude-sonnet-4-6, gpt-4o, llama3.2).",
        "git_repo_help": "İzlenecek Git deposu yolu (birden fazla eklenebilir).",
        "no_git_help": "Git aktiviteleri ve branch durumunu taramayı devre dışı bırakır.",
        "no_history_help": "Önceki günlerin brifing hafızasını devre dışı bırakır.",
        "interactive_help": "Brifing sonrasında etkileşimli ajan menüsünü açar.",
        "eod_help": "Gün Sonu Kapanışı (End-of-Day): Sabahki öncelikleri commit'ler ve notlarla mutabakat eder.",
        "voice_help": "Sesli yönetici brifingi üretir ve oynatır.",
        "mcp_help": "Cursor, Windsurf, Claude Desktop için MCP (Model Context Protocol) stdio sunucusu olarak çalıştırır.",
        "cli_doc": "Kişisel yapay zeka geliştirici asistanınız. Çoklu-LLM, yerel Ollama, Git algılı ve kalıcı hafızalı.",
        "api_key_prompt": "{provider} API anahtarınız",
        "api_key_empty": "API anahtarı boş olamaz.",
        "api_key_read_error": "API ayarı okunamadı: {path} ({error})",
        "api_key_write_error": "API ayarı kaydedilemedi: {path} ({error})",
        "api_key_missing_noninteractive": (
            "{env_var} bulunamadı ve terminal etkileşimli değil.\n"
            "PowerShell'de ayarlayın: $env:{env_var}='your_api_key'\n"
            "veya bash/zsh: export {env_var}='your_api_key'"
        ),
        "api_key_missing_error": (
            "ANTHROPIC_API_KEY bulunamadı. Önce API anahtarını ayarlayın:\n"
            "PowerShell: $env:ANTHROPIC_API_KEY='your_api_key'\n"
            "cmd.exe: set ANTHROPIC_API_KEY=your_api_key"
        ),
        "no_notes_for_summary": "Özet üretmek için not bulunamadı.",
        "rate_limit_error": "API rate limit hatası. Biraz bekleyip tekrar deneyin.",
        "connection_error": "API bağlantı hatası. İnternet bağlantınızı ve ağ erişiminizi kontrol edin.",
        "api_error": "API hatası: {error}",
        "empty_brief_error": "API boş bir özet döndü.",
        "git_banner": "Git Durumu: {banner}",
        "history_banner": "Hafıza: Önceki brifingden ({date}) görev devamlılığı sağlandı",
        "interactive_hint": "[c] Standup Kopyala  •  [s] MD Kaydet  •  [b] Görevi Böl  •  [g] Dal Aç  •  [r] Düzelt  •  [Enter] Çık",
        "clipboard_success": "Standup metni panoya kopyalandı!",
        "clipboard_failure": "Sistem panosuna erişilemedi.",
        "export_success": "Brifing kaydedildi: {path}",
        "break_down_prompt": "Bölünecek görev numarasını girin (1-{max_num}) veya görev metni yazın:",
        "break_down_success": "Görev planı şuraya eklendi: {path}",
        "no_tasks_to_break": "Bölünecek öncelikli görev bulunamadı.",
        "branch_confirm_prompt": "'{repo}' deposunda '{branch}' dalı oluşturulup geçilsin mi? [Y/n]:",
        "branch_success": "'{repo}' içinde '{branch}' dalına geçildi!",
        "branch_failure": "Dal oluşturulamadı: {error}",
        "no_repo_for_branch": "Dal açmak için uygun bir Git deposu bulunamadı.",
        "refine_prompt": "Düzeltme talimatını girin (ör. '2. görevi çıkar, auth hatasını öne al'):",
        "refine_success": "Güncellenen brifing hafızaya kaydedildi!",
        "eod_no_brief": "Bugüne ait sabah brifingi bulunamadı. Önce sabah önceliklerini oluşturmak için 'dailybrief' çalıştırın.",
        "eod_saved": "Gün sonu mutabakatı kaydedildi: {path}",
        "voice_unavailable": "Ses sentezleme kullanılamıyor (ses motoru veya API bulunamadı).",
        "force_help": "Anlık önbelleği atlayarak yapay zeka ile taze brifing üretir.",
        "schedule_help": "Belirtilen saatte (SS:DD ör. 08:45) otonom günlük sabah brifingi zamanlar.",
        "unschedule_help": "Zamanlanmış otonom sabah brifingi görevini kaldırır.",
        "background_help": "Sessiz arka plan modunda çalışır, önbelleği ısıtır ve masaüstü bildirimi gönderir.",
        "doctor_help": "Sistem tanılamasını çalıştırarak yapılandırma, API anahtarları, Git ve önbelleği kontrol eder.",
        "redact_pii_help": "Kimlik bilgilerine ek olarak e-posta ve IP adreslerini de sansürler.",
        "no_todos_help": "Kod içi TODO/FIXME yorumlarını taramayı devre dışı bırakır.",
        "weekly_help": "Haftalık sprint retrospektifi ve hız puan kartı üretir.",
        "init_shell_help": "bash, zsh, powershell veya fish için kabuk otomatik selamlama kancası üretir.",
    },
}

SYSTEM_PROMPTS: dict[str, str] = {
    "en": (
        "You are an executive developer assistant and personal Chief of Staff turning raw notes and engineering context into a crisp, high-signal daily briefing.\n"
        "Input notes may be in Turkish, English, or mixed. Always produce the briefing strictly in English.\n"
        "If Git context, previous day's briefing history, or chronic blocker alerts are provided, connect the dots:\n"
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
        "Eğer Git durumu, dünün brifing hafızası veya tıkanıklık uyarıları verildiyse:\n"
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
