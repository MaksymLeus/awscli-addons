#!/usr/bin/env bash
set -euo pipefail

# =======================================
# AWSCLI-Addons Installer
# Downloads prebuilt binary from GitHub releases
# Works on Linux and macOS
# =======================================

REPO="MaksymLeus/awscli-addons"      # GitHub repo
BINARY_NAME="awscli-addons" # Name of the binary
INSTALL_DIR="${HOME}/.local/bin"  # Default install dir

# Detect OS & Architecture
OS="$(uname | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$ARCH" in
    x86_64|amd64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *) echo "❌ Unsupported architecture: $ARCH"; exit 1 ;;
esac

echo "ℹ️ Detected OS: $OS, ARCH: $ARCH"

# Determine latest release URL
LATEST_URL="https://api.github.com/repos/$REPO/releases/latest"
DOWNLOAD_URL=$(curl -s $LATEST_URL | grep "browser_download_url" | grep "$OS-$ARCH" | cut -d '"' -f 4)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "❌ Could not find a prebuilt binary for $OS/$ARCH in latest release"
    exit 1
fi

echo "📦 Downloading binary from $DOWNLOAD_URL..."

TMP_FILE="$(mktemp)"
curl -L -o "$TMP_FILE" "$DOWNLOAD_URL"

# Ensure install dir exists
mkdir -p "$INSTALL_DIR"

# Move binary
mv "$TMP_FILE" "$INSTALL_DIR/$BINARY_NAME"
chmod +x "$INSTALL_DIR/$BINARY_NAME"

echo "✅ Installed $BINARY_NAME to $INSTALL_DIR"

# Add to PATH if not already
if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
    SHELL_RC=""
    if [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    if [ -n "$SHELL_RC" ]; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
        echo "ℹ️ Added $INSTALL_DIR to PATH in $SHELL_RC (reload shell or run 'source $SHELL_RC')"
    else
        echo "⚠️ Please add $INSTALL_DIR to your PATH manually"
    fi
fi

# Test binary
if command -v "$BINARY_NAME" &>/dev/null; then
    echo "🎉 $BINARY_NAME is ready! Run '$BINARY_NAME --help' to get started."
else
    echo "❌ Installation seems to have failed."
    exit 1
fi
