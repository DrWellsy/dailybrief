# DailyBrief Zero-Python Standalone Binary Installer (Windows PowerShell)
# Usage:
#   irm https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo = "DrWellsy/dailybrief"
$TargetDir = "$HOME\.dailybrief\bin"
$BinaryName = "dailybrief-windows-x64.exe"
$Dest = "$TargetDir\dailybrief.exe"
$DownloadUrl = "https://github.com/$Repo/releases/latest/download/$BinaryName"

Write-Host "⚡ Installing DailyBrief standalone executable for Windows..." -ForegroundColor Cyan

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

Write-Host "⬇️ Downloading $BinaryName from GitHub Releases..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $Dest -UseBasicParsing
} catch {
    Write-Error "Failed to download $BinaryName from $DownloadUrl. $_"
    exit 1
}

Write-Host "✔ DailyBrief binary installed to: $Dest" -ForegroundColor Green

# Ensure target directory is in user PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$TargetDir*") {
    $NewPath = if ($UserPath) { "$UserPath;$TargetDir" } else { $TargetDir }
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    $env:Path = "$env:Path;$TargetDir"
    Write-Host "✔ Added $TargetDir to User PATH environment variable." -ForegroundColor Green
}

Write-Host "`n🚀 Installation complete! Run 'dailybrief --help' to start." -ForegroundColor Cyan
