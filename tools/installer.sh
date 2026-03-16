#!/usr/bin/env bash
set -euo pipefail

# =======================================
# AWSCLI-Addons Production Installer
# Binary (preferred) → Python fallback
# Supports VERSION=1.2.3
# Supports BINARY_ONLY / PYTHON_ONLY
# =======================================

PROJECT_NAME="awscli-addons"
REPO="MaksymLeus/awscli-addons"
INSTALL_DIR="${HOME}/.local/bin"
# Global variables
VERSION="${VERSION:-latest}"; VERSION=${VERSION#v}

BINARY_ONLY="${BINARY_ONLY:-false}"
PYTHON_ONLY="${PYTHON_ONLY:-false}"
# track temp files for the cleanup trap
TMP_FILE=""
TMP_SUM=""
# ------------------------
# Helpers
# ------------------------
command_exists() { command -v "$1" >/dev/null 2>&1; }

cleanup() {
  # The '|| true' ensures that even if the file is missing, the command succeeds
  [ -n "${TMP_FILE:-}" ] && rm -f "$TMP_FILE" || true
  [ -n "${TMP_SUM:-}" ] && rm -f "$TMP_SUM" || true
}
# Single trap for the entire script execution
trap cleanup EXIT

fail() {
  echo "❌ $1"
  exit 1
}

info() { echo "ℹ️  $1"; }
success() { echo "✅ $1"; }


# ------------------------
# Colors for the UI
# ------------------------
if [ -t 1 ]; then
    BOLD="$(tput bold 2>/dev/null || echo '')"
    CYAN="$(tput setaf 6 2>/dev/null || echo '')"
    GREEN="$(tput setaf 2 2>/dev/null || echo '')"
    RESET="$(tput sgr0 2>/dev/null || echo '')"
else
    BOLD=""
    CYAN=""
    GREEN=""
    RESET=""
fi

# ------------------------
# Banners
# ------------------------
show_success_banner() {
  # Only clear if we are in a real terminal (TTY)
  [ -t 1 ] && clear

  # 2. Show the ASCII art
  echo -e "${CYAN}${BOLD}"
  cat << "EOF"

     ___   ____    __    ____   _______.  ______  __       __            ___       _______   _______   ______   .__   __.      _______.
    /   \  \   \  /  \  /   /  /       | /      ||  |     |  |          /   \     |       \ |       \ /  __  \  |  \ |  |     /       |
   /  ^  \  \   \/    \/   /  |   (----`|  ,----'|  |     |  |  ______ /  ^  \    |  .--.  ||  .--.  |  |  |  | |   \|  |    |   (----`
  /  /_\  \  \            /    \   \    |  |     |  |     |  | |______/  /_\  \   |  |  |  ||  |  |  |  |  |  | |  . `  |     \   \    
 /  _____  \  \    /\    / .----)   |   |  `----.|  `----.|  |       /  _____  \  |  '--'  ||  '--'  |  `--'  | |  |\   | .----)   |   
/__/     \__\  \__/  \__/  |_______/     \______||_______||__|      /__/     \__\ |_______/ |_______/ \______/  |__| \__| |_______/    
                                                                                                                                       
EOF

  # 3. Rest of success logic...
  echo -e "${RESET}"
  echo -e "${GREEN}${BOLD}Successfully installed ${PROJECT_NAME}!${RESET}"
  echo "--------------------------------------------------------"
  echo -e "📂 Location:  ${INSTALL_DIR}/${PROJECT_NAME}"
  echo -e "🚀 Direct Command:   ${BOLD}${PROJECT_NAME} --help${RESET}"

  # Check if AWS CLI is installed to show the Alias message
  if command_exists aws; then
      success "AWS CLI detected! Alias 'aws addons' is now active."
      echo -e "☁️  AWS Alias: ${CYAN}${BOLD}aws addons --help${RESET}"
  else
      echo -e "💡 ${CYAN}Tip: Install AWS CLI v2 to use the 'aws addons' alias.${RESET}"
  fi


  # Path & Reload instructions
  RC_FILE="${SHELL_RC:-~/.bashrc}"
  if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
      echo -e "\n⚠️  ${BOLD}ACTION REQUIRED:${RESET} To enable the command, run:"
      echo -e "   ${CYAN}source ${RC_FILE}${RESET}"
  else
      echo -e "\n✨ ${BOLD}Ready!${RESET} If the command is not found, run:"
      echo -e "   ${CYAN}source ${RC_FILE}${RESET}"
  fi
  echo "--------------------------------------------------------"
}


# ------------------------
# Detect OS / ARCH
# ------------------------
OS="$(uname | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$OS" in
  linux) OS="linux" ;;
  darwin) OS="macos" ;;
  *) fail "Unsupported OS: $OS" ;;
esac

case "$ARCH" in
  x86_64|amd64) ARCH="amd64" ;;
  aarch64|arm64) ARCH="arm64" ;;
  *) fail "Unsupported architecture: $ARCH" ;;
esac

info "Detected: $OS/$ARCH"

# ------------------------
# Resolve Release URL
# ------------------------
resolve_release_url() {
  command_exists curl || fail "curl is required for binary installation"

  if [ "$VERSION" = "latest" ]; then
    API_URL="https://api.github.com/repos/$REPO/releases/latest"
  else
    API_URL="https://api.github.com/repos/$REPO/releases/tags/v$VERSION"
  fi

  RELEASE_DATA=$(curl -fsSL "$API_URL" || fail "GitHub API unreachable")

  if command_exists jq; then
    DOWNLOAD_URL=$(echo "$RELEASE_DATA" | jq -r \
      --arg pattern "${OS}-${ARCH}" \
      '.assets[] | select(.name | contains($pattern)) | .browser_download_url' | head -n1)
    
    CHECKSUM_URL=$(echo "$RELEASE_DATA" | jq -r \
      '.assets[] | select(.name == "checksums.txt") | .browser_download_url' | head -n1)

    [ "$DOWNLOAD_URL" = "null" ] && DOWNLOAD_URL=""
    [ "$CHECKSUM_URL" = "null" ] && CHECKSUM_URL=""
  else
    # Fallback to grep (ensure it doesn't fail the script if nothing is found)
    DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep -o "https://[^\"]*${OS}-${ARCH}[^\"]*" | head -n1 || true)
    CHECKSUM_URL=$(echo "$RELEASE_DATA" | grep -o "https://[^\"]*checksums.txt[^\"]*" | head -n1 || true)
  fi

  if [ -z "$DOWNLOAD_URL" ]; then
    info "Could not find a pre-compiled binary for $OS-$ARCH."
    return 1
  fi
  if [ -z "$CHECKSUM_URL" ]; then
    info "No checksum file found in release. Skipping verification."
  fi

  return 0
}

# ------------------------
# Checksum validation
# ------------------------
verify_checksum() {
  [ -z "${CHECKSUM_URL:-}" ] && {
    info "No checksum file found, skipping verification"
    return 0
  }

  info "Verifying checksum..."
  TMP_SUM="$(mktemp)" # Assigned to the global variable

  if ! curl -fsSL "$CHECKSUM_URL" -o "$TMP_SUM"; then
    fail "Failed to download checksum file"
  fi

  FILENAME=$(basename "$DOWNLOAD_URL")
  EXPECTED=$(awk -v file="$FILENAME" '$2==file {print $1}' "$TMP_SUM")

  [ -z "$EXPECTED" ] && {
    info "Could not find checksum for $FILENAME in checksum file. Skipping."
    return 0
  }

	if command_exists sha256sum; then
			ACTUAL=$(sha256sum "$TMP_FILE" | awk '{print $1}')
	else
			ACTUAL=$(shasum -a 256 "$TMP_FILE" | awk '{print $1}')
	fi

  [ "$EXPECTED" != "$ACTUAL" ] && fail "Checksum verification failed! (Expected: $EXPECTED, Actual: $ACTUAL)"

  success "Checksum verified"
}

# ------------------------
# Binary installation
# ------------------------
install_binary() {
  info "Resolving release..."
  resolve_release_url || return 1

  info "Downloading binary..."
  TMP_FILE="$(mktemp)" # Assigned to the global variable

  if ! curl -fsSL -L -o "$TMP_FILE" "$DOWNLOAD_URL"; then
    return 1
  fi

  verify_checksum || return 1

  mkdir -p "$INSTALL_DIR"
  mv "$TMP_FILE" "$INSTALL_DIR/$PROJECT_NAME"
  chmod +x "$INSTALL_DIR/$PROJECT_NAME"

  success "Installed to $INSTALL_DIR/$PROJECT_NAME"
  
	# Set TMP_FILE to empty so cleanup doesn't try to delete the moved binary
  TMP_FILE="" 
}

# ------------------------
# Python fallback
# ------------------------
install_python() {
  if command_exists python3; then
    PYTHON=python3
  elif command_exists python; then
    PYTHON=python
  else
    fail "Python not found"
  fi

  if ! $PYTHON -m pip --version >/dev/null 2>&1; then
    info "Installing pip..."
    curl -fsSL https://bootstrap.pypa.io/get-pip.py | $PYTHON -
  fi

  info "Installing via pip..."
  INSTALL_SOURCE="git+https://github.com/$REPO.git"
  [ "$VERSION" != "latest" ] && INSTALL_SOURCE="${INSTALL_SOURCE}@$VERSION"

  $PYTHON -m pip install --user --upgrade "$INSTALL_SOURCE"
  success "Installed via Python"
}

# ------------------------
# Add to PATH if not already
# ------------------------
add_path() {
  local current_home="${HOME:-/root}"
  local SHELL_RC=""
  
  # Search for the best available RC file
  for f in ".zshrc" ".bashrc" ".bash_profile" ".profile"; do
    [ -f "$current_home/$f" ] && SHELL_RC="$current_home/$f" && break
  done

  # Default to .profile for Alpine/Docker if none exist
  [ -z "$SHELL_RC" ] && SHELL_RC="$current_home/.profile" && touch "$SHELL_RC"

  # 1. Exact match check for current session
  case ":$PATH:" in
    *":$INSTALL_DIR:"*)
      success "$INSTALL_DIR is already in PATH."
      return 0
      ;;
  esac

  # 2. Exact match check for the RC file content
  if grep -Fq "PATH=\"$INSTALL_DIR:\$PATH\"" "$SHELL_RC" >/dev/null 2>&1; then
    info "PATH export already exists in $SHELL_RC."
  else
    echo -e "\nexport PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
    success "Added $INSTALL_DIR to PATH in $SHELL_RC"
  fi

  info "To activate, run: source $SHELL_RC"
}

# ------------------------
# Add AWS cli alias (aws addons <commands>)
# ------------------------
add_awscli_alias() {
  info "Configuring AWS CLI alias..."
  
  local current_home="${HOME:-/root}"
  local alias_dir="$current_home/.aws/cli"
  local alias_file="$alias_dir/alias"
  
  # Ensure the directory exists
  mkdir -p "$alias_dir"
  touch "$alias_file"
  
  # Ensure the [toplevel] section exists
  grep -q "\[toplevel\]" "$alias_file" || echo -e "\n[toplevel]" >> "$alias_file"

  if ! grep -q "addons =" "$alias_file"; then
    echo "addons = !${PROJECT_NAME}" >> "$alias_file"
    success "Alias 'aws addons' configured."
  fi
}

# ------------------------
# Check Existing Install
# ------------------------
check_existing_install() {
  if command_exists "$PROJECT_NAME"; then
    CURRENT_V=$("$PROJECT_NAME" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
    if [ "$VERSION" != "latest" ] && [ "$VERSION" = "$CURRENT_V" ]; then
      success "$PROJECT_NAME $VERSION is already installed. Skipping."
      exit 0
    fi
  fi
}

# =======================================
# Installation Flow
# =======================================

check_existing_install

if [ "$PYTHON_ONLY" = "true" ]; then
    install_python
elif [ "$BINARY_ONLY" = "true" ]; then
    install_binary || fail "Binary installation failed."
else
    # 2. Smart Fallback: Try binary first, then python
    if ! install_binary; then
        info "Binary unavailable or incompatible, falling back to Python..."
        install_python
    fi
fi

add_path
add_awscli_alias

# Skip banner if in Docker, CI, or non-interactive shell
if [ -f /.dockerenv ] || [ "${CI:-}" = "true" ] || [ ! -t 1 ]; then
  info "Installation complete."
else
  show_success_banner
fi

exit 0
