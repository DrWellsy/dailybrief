from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

from rich.console import Console
from rich.text import Text

if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dailybrief.blockers import extract_priorities_from_brief
from dailybrief.memory import HISTORY_DIR

DEFAULT_VOICE_FILE = HISTORY_DIR / "latest_brief.mp3"


def clean_markdown_for_speech(text: str) -> str:
    # Remove markdown headers #, bold **, italic *, code blocks ```, inline code `, links [text](url)
    cleaned = re.sub(r"```[\s\S]*?```", "", text)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"[\#\*\_\~\>\•\-\|]", " ", cleaned)
    # Remove digits at beginning of lines like 1. 2)
    cleaned = re.sub(r"^\s*\d+[\.\)]\s*", "", cleaned, flags=re.MULTILINE)
    # Collapse multiple whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def generate_voice_script(brief_text: str, date_str: str, lang: str = "en") -> str:
    is_tr = lang.lower() == "tr"
    priorities = extract_priorities_from_brief(brief_text)

    # Extract follow-ups / things not to forget
    follow_ups: list[str] = []
    lines = brief_text.splitlines()
    in_follow = False
    for line in lines:
        cleaned = line.strip().lower()
        if any(h in cleaned for h in ("things not to forget", "unutulmaması", "unutulmamasi", "follow-ups")):
            in_follow = True
            continue
        if in_follow:
            m = re.match(r"^(?:\d+[\.\)]|[\-\*\•])\s+(.+)$", line.strip())
            if m:
                follow_ups.append(clean_markdown_for_speech(m.group(1)))

    clean_priorities = [clean_markdown_for_speech(p) for p in priorities[:3]]
    clean_follow = [clean_markdown_for_speech(f) for f in follow_ups[:2]]

    if is_tr:
        p_text = ". Birinci öncelik: " + ", ardından: ".join(clean_priorities) if clean_priorities else "Öncelikli görev bulunmuyor"
        f_text = " Hatırlatma: " + ", ".join(clean_follow) + "." if clean_follow else ""
        return (
            f"Günaydın. {date_str} tarihli DailyBrief sesli özetiniz.{p_text}.{f_text} "
            "Verimli ve odaklı bir gün dilerim."
        )
    else:
        p_text = ". Your top priorities are: " + ", followed by: ".join(clean_priorities) if clean_priorities else "No top priorities listed"
        f_text = " Key reminder: " + ", ".join(clean_follow) + "." if clean_follow else ""
        return (
            f"Good morning. Here is your DailyBrief for {date_str}.{p_text}.{f_text} "
            "Have a productive day."
        )


def synthesize_openai_speech(
    script: str,
    output_path: Path,
    api_key: str | None = None,
    voice: str = "alloy",
) -> bool:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return False

    url = "https://api.openai.com/v1/audio/speech"
    payload = {
        "model": "tts-1",
        "input": script,
        "voice": voice,
        "response_format": "mp3",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(resp.read())
            return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def synthesize_system_speech(script: str, output_path: Path) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean_text = script.replace('"', '\\"').replace("'", " ")

    if sys.platform == "win32":
        # Windows PowerShell SAPI voice
        ps_cmd = (
            f'$v = New-Object -ComObject SAPI.SpVoice; '
            f'$stream = New-Object -ComObject SAPI.SpFileStream; '
            f'$stream.Open("{output_path}", 3); '
            f'$v.AudioOutputStream = $stream; '
            f'$v.Speak("{clean_text}"); '
            f'$stream.Close();'
        )
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=15)
            if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                return True
        except (subprocess.SubprocessError, OSError):
            pass

    elif sys.platform == "darwin" and shutil.which("say"):
        # macOS say command
        try:
            res = subprocess.run(["say", "-o", str(output_path), script], capture_output=True, timeout=15)
            return res.returncode == 0
        except (subprocess.SubprocessError, OSError):
            pass

    elif sys.platform.startswith("linux") and shutil.which("espeak"):
        # Linux espeak command
        try:
            res = subprocess.run(["espeak", "-w", str(output_path), script], capture_output=True, timeout=15)
            return res.returncode == 0
        except (subprocess.SubprocessError, OSError):
            pass

    return False


def synthesize_brief_audio(
    script: str,
    output_path: Path | None = None,
    provider: str = "auto",
    openai_key: str | None = None,
    voice: str = "alloy",
) -> tuple[Path | None, str]:
    target = output_path or DEFAULT_VOICE_FILE
    chosen_provider = provider.lower().strip()

    # 1. Try OpenAI TTS if requested or auto with key
    if chosen_provider in ("openai", "auto"):
        mp3_target = target.with_suffix(".mp3")
        if synthesize_openai_speech(script, mp3_target, api_key=openai_key, voice=voice):
            return mp3_target, "openai"
        if chosen_provider == "openai":
            return None, "openai_failed"

    # 2. Try System offline TTS (Windows SAPI / macOS say / Linux espeak)
    wav_target = target.with_suffix(".wav")
    if synthesize_system_speech(script, wav_target):
        return wav_target, "system"

    return None, "unavailable"


def play_audio_file(file_path: Path, console: Console | None = None) -> bool:
    if not file_path.exists():
        return False

    c = console or Console()
    c.print(Text("🎙️ [Voice Briefing] Playing audio... (Press Ctrl+C to skip)", style="bold cyan"))

    try:
        if sys.platform == "win32":
            # Play using PowerShell SoundPlayer for WAV or Media.MediaPlayer for MP3
            abs_p = str(file_path.resolve())
            if file_path.suffix.lower() == ".wav":
                cmd = f'(New-Object Media.SoundPlayer "{abs_p}").PlaySync()'
            else:
                cmd = (
                    f'$p = New-Object System.Windows.Media.MediaPlayer; '
                    f'$p.Open([System.Uri]"{abs_p}"); '
                    f'$p.Play(); '
                    f'Start-Sleep -Seconds 12;'
                )
            subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, check=False)
            return True
        elif sys.platform == "darwin" and shutil.which("afplay"):
            subprocess.run(["afplay", str(file_path)], capture_output=True, check=False)
            return True
        elif sys.platform.startswith("linux"):
            for player in ("aplay", "paplay", "mpg123", "ffplay"):
                if shutil.which(player):
                    subprocess.run([player, str(file_path)], capture_output=True, check=False)
                    return True
    except KeyboardInterrupt:
        c.print(Text("⏩ Audio playback skipped.", style="dim yellow"))
        return True
    except (subprocess.SubprocessError, OSError):
        pass

    return False
