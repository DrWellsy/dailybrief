#!/usr/bin/env bash
# DailyBrief Zero-Python Standalone Binary Installer (macOS & Linux)
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/DrWellsy/dailybrief/main/install.sh | bash

set -e

REPO="DrWellsy/dailybrief"
INSTALL_DIR="${HOME}/.local/bin"

echo "⚡ Installing DailyBrief standalone binary..."

# Detect OS and architecture
OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
    Darwin)
        TARGET="dailybrief-macos-arm64"
        ;;
    Linux)
        TARGET="dailybrief-linux-x64"
        ;;
    *)
        echo "❌ Unsupported operating system: ${OS}"
        exit 1
        ;;
esac

mkdir -p "${INSTALL_DIR}"
DOWNLOAD_URL="https://github.com/${REPO}/releases/latest/download/${TARGET}"
DEST="${INSTALL_DIR}/dailybrief"

echo "⬇️ Downloading ${TARGET} from GitHub Releases..."
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "${DOWNLOAD_URL}" -o "${DEST}"
elif command -v wget >/dev/null 2>&1; then
    wget -qO "${DEST}" "${DOWNLOAD_URL}"
else
    echo "❌ Error: Neither curl nor wget found."
    exit 1
fi

chmod +x "${DEST}"

echo "✔ DailyBrief installed successfully to ${DEST}!"

# Verify PATH
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo ""
    echo "💡 Add ${INSTALL_DIR} to your PATH to run 'dailybrief' from anywhere:"
    echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc # or ~/.zshrc"
    echo "   source ~/.bashrc # or source ~/.zshrc"
fi

echo ""
echo "🚀 Run 'dailybrief --help' to get started!"
