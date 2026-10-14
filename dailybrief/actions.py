from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def copy_to_clipboard(text: str) -> bool:
    try:
        if sys.platform == "win32":
            proc = subprocess.run(["clip"], input=text, text=True, check=False)
            return proc.returncode == 0
        elif sys.platform == "darwin" and shutil.which("pbcopy"):
            proc = subprocess.run(["pbcopy"], input=text, text=True, check=False)
            return proc.returncode == 0
        elif sys.platform.startswith("linux"):
            if shutil.which("wl-copy"):
                proc = subprocess.run(["wl-copy"], input=text, text=True, check=False)
                return proc.returncode == 0
            elif shutil.which("xclip"):
                proc = subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=False)
                return proc.returncode == 0
    except (subprocess.SubprocessError, OSError):
        pass

    return False


def export_brief(brief: str, date_str: str, output_dir: Path | str | None = None) -> Path:
    target_dir = Path(output_dir) if output_dir else Path.cwd()
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"brief-{date_str}.md"
    file_path = target_dir / filename
    content = f"# Daily Brief - {date_str}\n\n{brief}\n"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def format_standup_text(brief: str, date_str: str, lang: str = "en") -> str:
    is_tr = lang.lower() == "tr"
    prefix = f"📅 *Günlük Standup ({date_str})*\n\n" if is_tr else f"📅 *Daily Standup ({date_str})*\n\n"

    # Clean any excessive blank lines while preserving bullets
    lines = [line.strip() for line in brief.splitlines() if line.strip()]
    return prefix + "\n".join(lines)
