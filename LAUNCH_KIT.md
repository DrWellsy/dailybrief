# 🚀 DailyBrief v0.3.0 Launch Kit & Social Media Assets

This kit contains ready-to-copy launch copy and announcements for LinkedIn, X (Twitter), Reddit, Product Hunt / Hacker News, and GitHub Releases.

---

## 💼 1. LinkedIn Launch Post

### 🇬🇧 English Version
```markdown
Every morning starts the same way for engineers: 5 scattered scratchpads, half-remembered Slack messages, and trying to recall what was committed yesterday before the first coffee kicks in.

Context switching was draining my focus. So I built an AI agent for my terminal: DailyBrief ⚡

Today, I’m releasing **DailyBrief v0.3.0** with enterprise-grade developer hardening:

🛡️ Built-in Local DLP Secret Redaction Firewall: We all paste temporary API keys, DB connection strings, and tokens into local scratchpads. DailyBrief automatically redacts sensitive credentials (sk-..., ghp_..., AIza..., JWTs, DB passwords) before any text leaves your machine for cloud LLMs.
🔍 Codebase TODO/FIXME Harvester: Don't keep separate markdown notes? DailyBrief automatically scans your watched Git repositories for inline `TODO:`, `FIXME:`, and `HACK:` comments, prioritizing files you modified recently.
📊 Real-Time Token, Cost & Latency Telemetry: Smart context budgeting prevents token crashes from massive lockfile diffs. Every briefing renders an exact cost footer (`⏱️ 1.2s │ 📊 ~1.1k in / 340 out │ 💰 Est: $0.0042 │ 🛡️ Firewall: Clean`).
📈 Weekly Sprint Retrospective (`dailybrief --weekly`): Synthesizes 7 days of Git commits and briefings into a Developer Velocity Scorecard (%) and ready-to-share Friday summary.
🚀 Zero-Friction Shell Startup Hook (`dailybrief --init-shell zsh`): Greets you automatically on your first morning terminal launch (checks today's brief and runs in 0ms on all subsequent tabs).
🔒 100% Local & Private Mode: Run completely offline with local Ollama (`llama3.2`, `mistral`) with zero API keys or external data transfer.
🔌 Native Model Context Protocol (MCP) Server: Connects your daily briefing, git status, and memory directly into Cursor, Claude Desktop, and Windsurf (`dailybrief --mcp`).
🌙 End-of-Day Reconciliation (`dailybrief --eod`): Automatically compares morning priorities against today’s commits and note checkboxes `[x]`.
📦 Zero-Python Standalone Binaries: Download standalone executables (`.exe` on Windows, native binaries on macOS & Linux) with a single curl/PowerShell command!

Install with one command:
• macOS & Linux: curl -fsSL https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.sh | bash
• Windows: irm https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.ps1 | iex

Check it out, star the repo, and let me know what you think! 🚀
🔗 https://github.com/DrWellsy/dailybrief

#Python #OpenSource #AI #SoftwareEngineering #DeveloperTools #Productivity #Terminal #MCP #Claude #Ollama #CyberSecurity #DLP
```

---

### 🇹🇷 Turkish Version (LinkedIn Türkiye Topluluğu İçin)
```markdown
Geliştiriciler olarak sabahları hep aynı senaryoyu yaşıyoruz: Farklı klasörlere dağılmış 5 ayrı karalama notu, dünden yarım kalan işler ve kahveyi yudumlamadan önce "Dün hangi repoda ne commit atmıştım?" sorusu.

Zihinsel dağınıklığı bitirmek için terminalde çalışan bir kişisel yapay zeka ajanı geliştirdim: DailyBrief ⚡

Bugün **DailyBrief v0.3.0** sürümünü kıdemli mühendislik ve güvenlik sertleştirmeleriyle yayınlıyorum! İşte yeni özellikler:

🛡️ Yerel DLP ve Gizli Bilgi Güvenlik Duvarı: Karalama notlarına geçici olarak yapıştırdığımız API anahtarları, DB bağlantı şifreleri ve JWT token'ları artık güvende! DailyBrief metinleri LLM'e göndermeden önce yerel regex güvenlik duvarından geçirerek hassas belirteçleri otomatik sansürler.
🔍 Kod İçi TODO/FIXME Hasadı: Ayrı not tutmayan geliştiriciler için izlenen Git depolarındaki `TODO:`, `FIXME:` ve `HACK:` yorumlarını son değiştirilen dosyalara öncelik vererek tarar ve brifinge ekler.
📊 Akıllı Bağlam Bütçesi & Maliyet/Gecikme Telemetrisi: Büyük lockfile farklarını kırparak bağlam taşmasını önler; brifingin altında kesin gecikme (`⏱️ 1.2s`), tahmini token ve dolar maliyetini (`💰 $0.0035`) gösterir.
📈 Haftalık Sprint Retrospektifi (`dailybrief --weekly`): Son 7 günün Git commit'lerini ve brifing hafızasını analiz ederek Geliştirici Hız Skorunu (%) ve Cuma günleri yöneticinizle paylaşabileceğiniz haftalık standup özetini üretir (`[c]` ile kopyalama).
🚀 Kabuk Otomatik Selamlama Kancası (`dailybrief --init-shell zsh`): Sabah terminalinizi ilk açtığınızda günde sadece bir kez brifingi çalıştırır (sonraki sekmelerde 0ms gecikme).
🔒 %100 Yerel ve Gizli Mod: API anahtarı olmadan yerel Ollama (Llama 3.2, Mistral) ile tamamen çevrimdışı çalıştırın.
🔌 Yerel MCP (Model Context Protocol) Desteği: `dailybrief --mcp` ile brifinginizi ve görev hafızanızı doğrudan Cursor, Claude Desktop ve Windsurf editörlerine bağlayın.
🌙 Gün Sonu Mutabakatı (`dailybrief --eod`): Sabah belirlenen hedefleri gün içindeki commit'ler ve notlardaki `[x]` işaretleriyle karşılaştırıp Tamamlanan, Devam Eden ve Yarına Aktarılan olarak otomatik raporlar.
📦 Python Gerektirmeyen İkili Dosyalar: Windows'ta doğrudan `.exe` veya macOS/Linux'ta tek komutla çalıştırın!

Tek komutla kurulum:
• macOS & Linux: curl -fsSL https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.sh | bash
• Windows: irm https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.ps1 | iex

GitHub üzerinden inceleyip yıldızlayabilir, görüşlerinizi paylaşabilirsiniz! 🚀
🔗 https://github.com/DrWellsy/dailybrief

#YazılımGeliştirme #AçıkKaynak #YapayZeka #Python #YazılımMühendisliği #GeliştiriciAraçları #Verimlilik #Terminal #CyberSecurity
```

---

## 🐦 2. X (Twitter) Launch Thread

**Tweet 1 (Hook):**
```text
I got tired of reviewing 5 scattered scratchpads and git logs before my morning coffee.

So I built DailyBrief ⚡ — an autonomous AI agent for your terminal that turns daily notes & multi-repo Git activity into a high-signal executive briefing.

And v0.3.0 with DLP secret firewall, code TODO harvester & weekly retro just dropped! 🧵👇
```

**Tweet 2 (Security & Code Harvester):**
```text
New in v0.3.0:
• 🛡️ Built-in Local DLP: Neutralizes API keys, JWTs & DB passwords before LLM transit
• 🔍 Harvester: Automatically scans inline `TODO:` & `FIXME:` code comments across repos
• 📊 Telemetry Footer: Real-time token usage, cost ($) & execution latency metrics
```

**Tweet 3 (Weekly Retro & Shell Hook):**
```text
• 📈 Weekly Retro (`--weekly`): Calculates Developer Velocity Score (%) & creates Friday standup updates
• 🚀 Shell Hook (`--init-shell`): Greets you automatically on first morning terminal launch (0ms on new tabs)
• 🔌 Native MCP Server (`--mcp`) for Cursor & Claude Desktop
• 🌙 End-of-Day reconciliation (`--eod`)
```

**Tweet 4 (Zero-Python Install):**
```text
No Python needed. Install the standalone single-file binary with one line:

macOS / Linux:
curl -fsSL https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.sh | bash

Windows (PowerShell):
irm https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.ps1 | iex
```

**Tweet 5 (Outro):**
```text
100% open source under MIT with 136 passing tests.

Check it out, star the repo, and level up your morning routine:
🔗 https://github.com/DrWellsy/dailybrief
```

---

## 👾 3. Hacker News (Show HN) / Reddit (r/Python, r/commandline)

**Title:**
`Show HN: DailyBrief v0.3.0 – Terminal AI assistant with local DLP firewall, code TODO harvester & Git radar`

**Body:**
```markdown
Hi everyone,

I built DailyBrief because my morning engineering routine had too much cognitive load: checking markdown scratchpads across different directories, recalling yesterday's git branches, and losing track of deferred tasks.

Today I'm releasing v0.3.0 addressing the exact concerns senior developers raise:
1. Local DLP Secret Redaction Firewall: Automatically detects and redacts API keys (Anthropic, OpenAI, Gemini, GitHub tokens, Slack), JWTs, database URLs, and private SSH keys from messy scratchpads before LLM transit.
2. Codebase TODO/FIXME Harvester: Scans your watched Git repositories for inline comments (`TODO:`, `FIXME:`, `HACK:`), prioritizing files sitting on your active branch.
3. Smart Context Budgeter & Cost Telemetry: Caps noisy lockfiles and renders live token counts, latency, and estimated USD cost footer ($0.0000 on Ollama).
4. Weekly Retrospective (`--weekly`): Synthesizes 7-day commits and briefs into a Developer Velocity Scorecard (%) and Slack Friday update.
5. Shell Auto-Greeting Hook: `dailybrief --init-shell <bash|zsh|powershell|fish>` greets you once per day on first terminal launch (0ms overhead on subsequent tabs).
6. Local-First & Private: Runs 100% offline with Ollama (`llama3.2`, `mistral`) or cloud providers (Anthropic, OpenAI, Gemini).
7. MCP Server Mode: Supports stdio JSON-RPC 2.0 (`dailybrief --mcp`) so Cursor, Claude Desktop, and Windsurf can query your priorities and git context as an agentic tool.
8. Standalone Binaries: Ships single-file binaries for Windows (.exe), macOS (arm64), and Linux (x64) via GitHub Actions.

GitHub: https://github.com/DrWellsy/dailybrief

Feedback, issues, and PRs are very welcome!
```

---

## 🏷️ 4. GitHub Release Notes (v0.3.0)

```markdown
# DailyBrief v0.3.0 — Hardened Security, Codebase Harvesting & Weekly Velocity

We are proud to release **DailyBrief v0.3.0**! This release brings enterprise-grade security hardening, codebase comment harvesting, real-time token telemetry, and weekly sprint retrospectives.

### 🌟 New in v0.3.0
- **🛡️ Local DLP & Secret Redaction Firewall (`dailybrief/security.py`):** Automatically scans all notes and git context before sending to cloud LLMs, redacting API keys (`sk-...`, `ghp_...`, `AIza...`), JWTs, database connection strings, and private SSH keys with a clear terminal security badge. Optional `--redact-pii` masks email and IP addresses.
- **🔍 Codebase `TODO` / `FIXME` Harvester (`dailybrief/todo_scanner.py`):** Automatically extracts inline code tasks from watched Git repos, prioritizing files modified recently or sitting on your active branch (`--no-todos` to disable).
- **📊 Smart Context Budgeter & Cost/Latency Telemetry (`dailybrief/telemetry.py`):** Enforces token budget safety by compressing lockfile diffs; renders sleek telemetry footer with latency (`⏱️ 1.2s`), token usage (`📊 ~1.1k in / 340 out`), estimated USD cost (`💰 $0.0042`), and firewall status.
- **📈 Weekly Sprint Retrospective & Velocity Engine (`dailybrief --weekly`):** Synthesizes the last 7 days of Git commits and briefings into a Developer Velocity Scorecard (%) with one-click clipboard copy (`[c]`) for Friday manager syncs.
- **🚀 Shell Auto-Greeting Hook (`dailybrief --init-shell <bash|zsh|powershell|fish>`):** Outputs a non-blocking startup script snippet that runs DailyBrief only once per day on first morning terminal launch (0ms overhead on subsequent tabs).

### 📦 Standalone Executable Binaries (Zero Python Required)
You can run DailyBrief on any machine without Python:
- **macOS & Linux:** `curl -fsSL https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.sh | bash`
- **Windows PowerShell:** `irm https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.ps1 | iex`

### 🧪 Test Suite & Quality
- **136 unit tests** passing with 100% pass rate across DLP redaction, todo scanner, telemetry, weekly velocity, caching, and CLI flags.
```
