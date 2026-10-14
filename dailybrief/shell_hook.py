from __future__ import annotations


def generate_shell_hook(shell_name: str, executable: str = "dailybrief") -> str:
    """Generates a lightweight, non-blocking shell startup hook.

    Ensures DailyBrief runs automatically only once per day on the first terminal launch.
    Subsequent terminal tabs check for today's brief file and return immediately in 0ms.
    """
    shell = shell_name.lower().strip()

    if shell in ("bash", "zsh", "sh"):
        target_file = "~/.zshrc" if shell == "zsh" else "~/.bashrc"
        return f"""# ==============================================================================
# DailyBrief Auto-Greeting Hook ({shell})
# Add this snippet to your {target_file} to receive morning briefings automatically:
# ==============================================================================
if command -v {executable} >/dev/null 2>&1; then
    _DB_TODAY=$(date +%Y-%m-%d)
    _DB_BRIEF="$HOME/.dailybrief/brief-$_DB_TODAY.md"
    if [ ! -f "$_DB_BRIEF" ]; then
        # First terminal launch of the day: run dailybrief
        {executable}
    fi
    unset _DB_TODAY _DB_BRIEF
fi
"""

    elif shell in ("powershell", "pwsh", "ps1"):
        return f"""# ==============================================================================
# DailyBrief Auto-Greeting Hook (PowerShell)
# Add this snippet to your PowerShell profile ($PROFILE):
# Notepad $PROFILE
# ==============================================================================
if (Get-Command {executable} -ErrorAction SilentlyContinue) {{
    $dbToday = (Get-Date).ToString("yyyy-MM-dd")
    $dbBrief = Join-Path $HOME ".dailybrief\\brief-$dbToday.md"
    if (-not (Test-Path $dbBrief)) {{
        # First terminal launch of the day: run dailybrief
        & {executable}
    }}
}}
"""

    elif shell == "fish":
        return f"""# ==============================================================================
# DailyBrief Auto-Greeting Hook (Fish)
# Add this snippet to ~/.config/fish/config.fish
# ==============================================================================
if type -q {executable}
    set -l _db_today (date +%Y-%m-%d)
    set -l _db_brief "$HOME/.dailybrief/brief-$_db_today.md"
    if not test -f "$_db_brief"
        # First terminal launch of the day: run dailybrief
        {executable}
    end
end
"""
    else:
        raise ValueError(
            f"Unsupported shell: '{shell_name}'. Supported shells: bash, zsh, powershell, fish"
        )
