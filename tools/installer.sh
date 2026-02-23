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
VERSION="${VERSION:-latest}"
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
  [ -n "${TMP_FILE:-}" ] && rm -f "$TMP_FILE"
  [ -n "${TMP_SUM:-}" ] && rm -f "$TMP_SUM"
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
BOLD="$(tput bold 2>/dev/null || echo '')"
CYAN="$(tput setaf 6 2>/dev/null || echo '')"
GREEN="$(tput setaf 2 2>/dev/null || echo '')"
RESET="$(tput sgr0 2>/dev/null || echo '')"

# ------------------------
# Banners
# ------------------------
show_success_banner() {
  # 1. Clear the screen to make the banner pop
  clear

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
      echo -e "💡 ${YELLOW}Tip: Install AWS CLI v2 to use the 'aws addons' alias.${NC}"
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
  if ! command_exists curl; then
    fail "curl is required for binary installation"
  fi

  if [ "$VERSION" = "latest" ]; then
    API_URL="https://api.github.com/repos/$REPO/releases/latest"
  else
    API_URL="https://api.github.com/repos/$REPO/releases/tags/v$VERSION"
  fi

	RELEASE_DATA=$(curl -fsSL "$API_URL" || fail "GitHub API unreachable")

  DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep -o "https://[^\"]*${OS}-${ARCH}[^\"]*" | head -n1 || true)
  CHECKSUM_URL=$(echo "$RELEASE_DATA" | grep -o "https://[^\"]*checksums.txt[^\"]*" | head -n1 || true)

  if [ -z "$DOWNLOAD_URL" ]; then
    info "Could not find a pre-compiled binary for $OS-$ARCH."
    return 1
  fi
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

  [ -z "$EXPECTED" ] && fail "Could not find checksum for $FILENAME in checksum file"

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

  if [ "$VERSION" = "latest" ]; then
    $PYTHON -m pip install --user "git+https://github.com/$REPO.git"
  else
    $PYTHON -m pip install --user "git+https://github.com/$REPO.git@$VERSION"
  fi

  success "Installed via Python"
}

# ------------------------
# Add to PATH if not already
# ------------------------
add_path() {
	# Check for the existence of RC files instead of shell variables
	SHELL_RC=""
	if [ -f "$HOME/.zshrc" ]; then
		SHELL_RC="$HOME/.zshrc"
	elif [ -f "$HOME/.bashrc" ]; then
		SHELL_RC="$HOME/.bashrc"
	elif [ -f "$HOME/.profile" ]; then
		SHELL_RC="$HOME/.profile"
	fi

	if ! echo "$PATH" | grep -Fq "$INSTALL_DIR"; then
		if [ -n "$SHELL_RC" ] && ! grep -Fxq "export PATH=\"$INSTALL_DIR:\$PATH\"" "$SHELL_RC"; then
			# Add a newline before the export to ensure it doesn't glue to the last line
			echo "" >> "$SHELL_RC" 
			echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
			info "Added $INSTALL_DIR to PATH in $SHELL_RC"
			info "Reload shell or run: source $SHELL_RC"
		else
			fail "Please add $INSTALL_DIR to your PATH manually"
		fi
	fi

}

# ------------------------
# Add AWS cli alias (aws addons <commands>)
# ------------------------
add_awscli_alias() {
  info "Configuring AWS CLI alias..."
  
  # Ensure the directory exists
  mkdir -p "$HOME/.aws/cli"
  
  local alias_file="$HOME/.aws/cli/alias"
  
  # Check if [toplevel] header exists, if not, create it
  if [ ! -f "$alias_file" ] || ! grep -q "\[toplevel\]" "$alias_file"; then
    echo "[toplevel]" >> "$alias_file"
  fi

  # Define the alias string (using "$@" to pass all arguments correctly)
  # We use a literal '$' for the variables so they aren't expanded during 'echo'
  local alias_cmd="addons = !f() { $INSTALL_DIR/$PROJECT_NAME \"\$@\"; }; f"

  # Append the alias if it's not already there
  if ! grep -q "addons =" "$alias_file"; then
    echo "$alias_cmd" >> "$alias_file"
    success "AWS CLI alias 'aws addons' configured!"
  else
    info "AWS CLI alias 'addons' already exists."
  fi
}




# ------------------------
# Check Existing Install
# ------------------------
check_existing_install() {
  if command_exists "$PROJECT_NAME"; then
    # Try to get the current version from the binary
    # Assumes your app supports --version
    CURRENT_V=$("$PROJECT_NAME" --version 2>/dev/null | awk '{print $NF}')
    
    if [ "$VERSION" = "latest" ]; then
      # If they want latest, we usually proceed unless you add 
      # a complex API check to compare CURRENT_V with GitHub's latest
      info "Found existing $PROJECT_NAME ($CURRENT_V). Updating to latest..."
    elif [ "v$VERSION" = "$CURRENT_V" ] || [ "$VERSION" = "$CURRENT_V" ]; then
      success "$PROJECT_NAME $VERSION is already installed. Skipping."
      exit 0
    fi
  fi
}

# ------------------------
# Installation Flow
# ------------------------

check_existing_install

if [ "$PYTHON_ONLY" = "true" ]; then
	info "Forced Python installation"
	install_python
	exit 0
fi

if [ "$BINARY_ONLY" = "true" ]; then
	info "Forced Binary installation"
	install_binary || fail "Binary installation failed"
	exit 0
fi

# Smart fallback
if install_binary; then
	success "Binary installation successful"
else
  info "Binary unavailable, falling back to Python..."
  install_python
fi

add_path
add_awscli_alias

# The Grand Finale
show_success_banner