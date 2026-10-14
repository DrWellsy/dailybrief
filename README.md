<div align="center">

# ⚡ DailyBrief

**Your personal AI executive developer assistant in the terminal.**  
Turn messy daily notes, git activity, and sprint tasks into a crisp, high-signal briefing with persistent memory.

[Türkçe Dokümantasyon (Turkish README)](README.tr.md) • [Report Bug](https://github.com/DrWellsy/dailybrief/issues) • [Request Feature](https://github.com/DrWellsy/dailybrief/issues)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-red)](https://github.com/sponsors/DrWellsy)

<br/>

![DailyBrief Demo](demo.gif)

</div>

---

## 💡 Why DailyBrief?

As developers and builders, we scatter notes everywhere: quick scratchpads, sprint priorities, Jira copies, and end-of-day reminders. When the day starts, reviewing 10 different files while recalling what you committed yesterday takes too much cognitive load.

**DailyBrief** acts as your personal terminal agent:
- 📂 **Multi-Source Ingestion:** Scans your local notes (`.md` & `.txt`) whether written in English, Turkish, or a mix.
- 🐙 **Git Context Sensing:** Automatically inspects active branch, recent commits (last 48h), and uncommitted working changes.
- 🧠 **Persistent Memory & Accountability:** Remembers yesterday's briefing to detect postponed or carried-over priorities.
- ⚡ **Interactive Terminal Actions:** One-click copy formatted standup updates to your clipboard (`[c]`) or export to Markdown (`[s]`).

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/DrWellsy/dailybrief.git
cd dailybrief
pip install -r requirements.txt
```

*(Optional) Install as an editable CLI command:*

```bash
pip install -e .
```

### 2. Configure Your API Key

DailyBrief uses Anthropic's Claude (`ANTHROPIC_API_KEY`).

**Linux / macOS:**
```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your_api_key_here"
```

> **Interactive Setup:** If no environment variable is found, DailyBrief prompts for your key on first run and securely saves it locally in `~/.dailybrief/config.toml`.

---

## 💻 Usage & Flags

```bash
dailybrief [OPTIONS]
```

Or via Python module:

```bash
python -m dailybrief [OPTIONS]
```

### Options & Flags

| Flag | Description | Default |
|------|-------------|---------|
| `-s, --source <PATH>` | Directory containing `.md` and `.txt` notes | `./notes` |
| `-l, --lang <en\|tr>` | Output and interface language | `en` |
| `-i, --interactive` | Prompt for actions after briefing (copy standup, export) | `false` |
| `--no-git` | Disable automatic git branch & commit scanning | `false` |
| `--no-history` | Disable previous briefing memory & follow-up tracking | `false` |
| `-h, --help` | Show command line options and exit | |

#### Examples

**Start morning routine with full interactive actions:**
```bash
dailybrief -i
```

**Generate a Turkish briefing from a custom Obsidian vault:**
```bash
dailybrief -s ~/Documents/ObsidianVault/Daily -l tr -i
```

---

## 🧠 How the Agent Works

```text
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Local Notes    │     │ Git Repository │     │ Memory History │
│ (.md & .txt)   │     │ (branch/status)│     │ (~/.dailybrief)│
└───────┬────────┘     └───────┬────────┘     └───────┬────────┘
        │                      │                      │
        └───────────────► 🤖 DailyBrief ◄─────────────┘
                               │
                      Anthropic Claude Sonnet
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │ ⚡ DailyBrief Executive Terminal Panel        │
        │                                              │
        │ 📌 Key Priorities for Today (3–5 items)      │
        │ ⚡ Things Not to Forget / Follow-ups         │
        └──────────────────────┬───────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
     [c] Copy Standup                     [s] Export to Markdown
     (System Clipboard)                   (brief-YYYY-MM-DD.md)
```

---

## 🧪 Testing

Run the full unit test suite with `pytest`:

```bash
pytest
```

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
