#!/usr/bin/env python3
"""Build script for standalone DailyBrief single-file binary using PyInstaller.

Usage:
    python scripts/build_binary.py
"""

from __future__ import annotations

import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def get_binary_name() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        arch = "x64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine

    if system == "windows":
        return f"dailybrief-windows-{arch}.exe"
    elif system == "darwin":
        return f"dailybrief-macos-{arch}"
    else:
        return f"dailybrief-linux-{arch}"


def build() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    entry_point = root_dir / "main.py"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"

    binary_name = get_binary_name()
    print(f"⚡ Building standalone DailyBrief binary: {binary_name}...")

    # Ensure pyinstaller is available
    pyinstaller = shutil.which("pyinstaller")
    if not pyinstaller:
        print("❌ PyInstaller not found. Installing pyinstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        pyinstaller = shutil.which("pyinstaller") or sys.executable

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "dailybrief",
        "--collect-all",
        "rich",
        "--collect-all",
        "dailybrief",
        "--hidden-import",
        "dailybrief.cli",
        "--hidden-import",
        "dailybrief.cache",
        "--hidden-import",
        "dailybrief.doctor",
        "--hidden-import",
        "dailybrief.scheduler",
        "--hidden-import",
        "dailybrief.mcp_server",
        "--hidden-import",
        "dailybrief.voice",
        "--hidden-import",
        "dailybrief.eod",
        "--hidden-import",
        "dailybrief.git_radar",
        "--hidden-import",
        "dailybrief.security",
        "--hidden-import",
        "dailybrief.todo_scanner",
        "--hidden-import",
        "dailybrief.telemetry",
        "--hidden-import",
        "dailybrief.weekly",
        "--hidden-import",
        "dailybrief.shell_hook",
        str(entry_point),
    ]

    print("Running command:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(root_dir))
    if proc.returncode != 0:
        print("❌ Build failed.")
        return proc.returncode

    # Locate generated binary
    output_bin = dist_dir / ("dailybrief.exe" if platform.system() == "Windows" else "dailybrief")
    target_bin = dist_dir / binary_name

    if output_bin.exists():
        if target_bin.exists():
            target_bin.unlink()
        output_bin.rename(target_bin)
        print(f"✔ Successfully built standalone binary: {target_bin} ({target_bin.stat().st_size / (1024*1024):.2f} MB)")
        return 0

    print(f"❌ Output binary not found at {output_bin}")
    return 1


if __name__ == "__main__":
    sys.exit(build())
