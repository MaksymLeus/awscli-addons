#!/usr/bin/env bash
set -euo pipefail

#========================================
# COLORS
#========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[1;34m'
NC='\033[0m'

#========================================
# CONFIGURATION
#========================================
PROJECT_NAME="awscli-addons"
SRC_DIR="awscli_addons"
DIST_DIR="dist"
BUILD_DIR="build"
# Set a default Python - will be refined by install_python_dep
PYTHON=$(command -v python3 || command -v python || echo "python3")
VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")

#========================================
# HELP 
#========================================
# Helper for cross-platform sed in-place
sed_inplace() {
  local pattern="$1"
  local file="$2"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS (BSD sed)
    sed -i "" "$pattern" "$file"
  else
    # Linux (GNU sed)
    sed -i "$pattern" "$file"
  fi
}

command_exists() { command -v "$1" >/dev/null 2>&1; }

#========================================
# HELP MESSAGE
#========================================
print_header() {
  echo -e "${BLUE}========================================================${NC}"
  echo -e "${BLUE}  ${PROJECT_NAME} Build System — Version: ${VERSION}${NC}"
  echo -e "${BLUE}========================================================${NC}"
}

help_msg() {
cat <<EOF
Usage:
  ./build.sh [command]

Commands:
  quick      Build onedir executable for the current system
  clean      Remove build artifacts
  zip      Zip the dist/${PROJECT_NAME}/ folder
  checksums    Generate SHA256 checksums for dist/${PROJECT_NAME}/
  help       Show this help message

Output:
  dist/${PROJECT_NAME}/     Onedir executable folder
EOF
}
#========================================
# Python + Dependencies
#========================================
install_python_dep() {
  echo -e "${YELLOW}📦 Checking dependencies...${NC}"

  if ! $PYTHON -m pip --version >/dev/null 2>&1; then
		echo -e "${YELLOW} Installing pip... ${NC}"

    curl -fsSL https://bootstrap.pypa.io/get-pip.py | $PYTHON -
  fi

  $PYTHON -m pip install --upgrade pip setuptools wheel >/dev/null

  # Extract dependencies from pyproject.toml
  # Improved sed logic to be more robust
  local deps
  deps=$(sed -e '1,/dependencies = \[/d' -e '/\]/,$d' pyproject.toml | tr -d '",' | xargs)
  
  if [ -n "$deps" ]; then
    echo -e "${YELLOW} Installing: $deps${NC}"
    $PYTHON -m pip install $deps
  fi

  $PYTHON -m pip install pyinstaller


}

#========================================
# BUILD FUNCTIONS
#========================================
build_quick() {
	# 1. Override the global VERSION if $1 is provided
	if [ -n "${1:-}" ]; then
			VERSION="$1"
	fi

	echo -e "${YELLOW}⚙️ Building onedir executable for current system...${NC}"

  # Inject Version
  sed_inplace "s/__version__ = .*/__version__ = \"$VERSION\"/" "$SRC_DIR/cli.py"

  # Build optimization flags
	export PYTHONDONTWRITEBYTECODE=1
	export PYTHONOPTIMIZE=1
	
	$PYTHON -m PyInstaller --onefile --name "$PROJECT_NAME" \
    --exclude-module tkinter --exclude-module unittest --exclude-module pydoc \
    --strip --noupx --clean \
    "$SRC_DIR/cli.py"
	
	# IMPORTANT: Force macOS to trust the onefile extraction
	if [[ "$OSTYPE" == "darwin"* ]]; then
			echo "🔒 Ad-hoc signing for macOS speed..."
			codesign --force --deep --sign - "dist/$PROJECT_NAME"
			xattr -d com.apple.quarantine "dist/$PROJECT_NAME" 2>/dev/null || true
	fi

	echo -e "${GREEN}✔ Build complete! Output folder: ${DIST_DIR}/${PROJECT_NAME}${NC}"
}

zip_dist() {
  local target="${DIST_DIR}/${PROJECT_NAME}"
  [ ! -f "$target" ] && { echo -e "${RED}❌ Binary not found.${NC}"; exit 1; }
  
  echo -e "${YELLOW}📦 Zipping binary...${NC}"
  zip -j "${PROJECT_NAME}.zip" "$target"
  echo -e "${GREEN}✔ Created ${PROJECT_NAME}.zip${NC}"
}

generate_checksums() {
  local target="${DIST_DIR}/${PROJECT_NAME}"
  [ ! -f "$target" ] && { echo -e "${RED}❌ Binary not found.${NC}"; exit 1; }
  
  echo -e "${YELLOW}🔐 Generating SHA256...${NC}"
  if command_exists sha256sum; then
    sha256sum "$target" > "${target}.sha256"
  else
    shasum -a 256 "$target" > "${target}.sha256"
  fi
  echo -e "${GREEN}✔ Checksum saved to ${target}.sha256${NC}"
}

clean() {
  echo -e "${YELLOW}🧹 Cleaning old builds...${NC}"
  rm -rf "$DIST_DIR" "$BUILD_DIR" "*.zip" "*.spec" "__pycache__"
}

#========================================
# MAIN LOGIC
#========================================
print_header

cmd="${1:-quick}"
case "$cmd" in
  quick)
    clean
		install_python_dep
    build_quick "${2:-}"
    ;;
  docker)
    build_docker "${2:-}" "${3:-}"
    ;;  
  clean)
    clean
    ;;
  zip)
    zip_dist
    ;;
  checksums)
    generate_checksums
    ;;
  help|--help|-h)
    help_msg
    ;;
  *)
    echo -e "${RED}Unknown command: $cmd${NC}"
    help_msg
    exit 1
    ;;
esac
