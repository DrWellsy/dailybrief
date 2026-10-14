<div align="center">

# ⚡ DailyBrief

**Your personal AI executive assistant in the terminal.**  
Turn messy daily notes, sprint items, and thoughts into a crisp, high-signal briefing.

[Türkçe Dokümantasyon (Turkish README)](README.tr.md) • [Report Bug](https://github.com/DrWellsy/dailybrief/issues) • [Request Feature](https://github.com/DrWellsy/dailybrief/issues)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-red)](https://github.com/sponsors/DrWellsy)

<br/>

![DailyBrief Demo](demo.gif)

</div>

---

## 💡 Why DailyBrief?

As developers and builders, we scatter notes everywhere: quick scratchpads, sprint priorities, Jira task copies, and end-of-day reminders. When the day starts, reviewing 10 different files takes too much cognitive load.

**DailyBrief** scans your local notes folder (Markdown `.md` and plain text `.txt`), analyzes them with Anthropic's Claude, and compiles an executive terminal briefing in seconds:

- **Key Priorities for Today** (3–5 actionable tasks you must tackle first)
- **Things Not to Forget / Follow-ups** (deadlines, meetings, customer follow-ups)

Even if your notes are written in a mix of Turkish and English, DailyBrief understands both seamlessly and outputs a coherent briefing in your preferred language (`--lang en` or `--lang tr`).

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Aloostor/dailybrief.git
cd dailybrief
pip install -r requirements.txt
```

*(Optional) Install as an editable CLI command:*

```bash
pip install -e .
```

### 2. Configure Your API Key

DailyBrief requires an Anthropic API key (`ANTHROPIC_API_KEY`).

**Linux / macOS:**
```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=your_api_key_here
```

> **First Run Prompt:** If no environment variable is found, the CLI interactively prompts for your key and safely stores it locally in `~/.dailybrief/config.toml`.

---

## 💻 Usage

Run against the default `./notes` folder:

```bash
python -m dailybrief
```

Or if installed via `pip install -e .`:

```bash
dailybrief
```

### Options & Flags

| Flag | Description | Default |
|------|-------------|---------|
| `-s, --source <PATH>` | Directory containing `.md` and `.txt` notes | `./notes` |
| `-l, --lang <en\|tr>` | Output and interface language | `en` |
| `-h, --help` | Show command line options and exit | |

#### Examples

**Generate a Turkish briefing from a custom notes folder:**
```bash
dailybrief -s ~/Documents/ObsidianVault/Daily -l tr
```

**Specify language in module mode:**
```bash
python -m dailybrief --source ./my-notes --lang en
```

---

## 🛠️ Project Structure

```text
dailybrief/
├── dailybrief/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py          # Click CLI & Rich terminal rendering
│   ├── i18n.py         # Multi-language messages & system prompts (en/tr)
│   ├── reader.py       # Robust note loader (UTF-8, Windows-1254 fallbacks)
│   └── summarizer.py   # Anthropic Claude API integration
├── notes/              # Sample markdown/txt notes
├── scripts/
│   └── generate_demo.py # Script to render modern demo.gif
├── tests/              # Pytest test suite
├── pyproject.toml
└── demo.gif
```

---

## 🧪 Testing

Run test suite with `pytest`:

```bash
pytest
```

---

## 🎨 Regenerating the Demo GIF

The demo animation in this repository is built using a standalone PIL-based terminal renderer with pixel-perfect Rich UI styling:

```bash
python scripts/generate_demo.py
```

---

## 🤝 Contributing

Contributions, feedback, and ideas are warmly welcomed!
Feel free to open an issue or submit a pull request.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
