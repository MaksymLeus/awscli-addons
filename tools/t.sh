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
PYTHON=$(command -v python3 || command -v python || echo "python3")
VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")

#========================================
# HELPERS
#========================================
sed_inplace() {
  local pattern="$1"
  local file="$2"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i "" "$pattern" "$file"
  else
    sed -i "$pattern" "$file"
  fi
}

command_exists() { command -v "$1" >/dev/null 2>&1; }

print_header() {
  echo -e "${BLUE}========================================================${NC}"
  echo -e "${BLUE}  ${PROJECT_NAME} Build System — Version: ${VERSION}${NC}"
  echo -e "${BLUE}========================================================${NC}"
}

help_msg() {
cat <<EOF
Usage:
  ./build.sh [command] [version] [image_tag]

Commands:
  quick        Build onedir executable for the current system
  docker       Build Docker image (args: version, image_tag)
  clean        Remove build artifacts
  zip          Zip the dist/${PROJECT_NAME} binary
  checksums    Generate SHA256 checksums
  help         Show this help message

Examples:
  ./build.sh quick v1.0.0
  ./build.sh docker feature/init my-repo/awscli-addons:latest
EOF
}

#========================================
# DEPENDENCIES
#========================================
install_python_dep() {
  echo -e "${YELLOW}📦 Checking dependencies...${NC}"
  if ! $PYTHON -m pip --version >/dev/null 2>&1; then
    curl -fsSL https://bootstrap.pypa.io/get-pip.py | $PYTHON -
  fi
  $PYTHON -m pip install --upgrade pip setuptools wheel >/dev/null
  
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
  local target_version="${1:-$VERSION}"
  echo -e "${YELLOW}⚙️ Building onedir executable for current system...${NC}"
  sed_inplace "s/__version__ = .*/__version__ = \"$target_version\"/" "$SRC_DIR/cli.py"

  export PYTHONDONTWRITEBYTECODE=1
  export PYTHONOPTIMIZE=1
  
  $PYTHON -m PyInstaller --onefile --name "$PROJECT_NAME" \
    --exclude-module tkinter --exclude-module unittest --exclude-module pydoc \
    --strip --noupx --clean \
    "$SRC_DIR/cli.py"
  
  if [[ "$OSTYPE" == "darwin"* ]]; then
      codesign --force --deep --sign - "dist/$PROJECT_NAME"
      xattr -d com.apple.quarantine "dist/$PROJECT_NAME" 2>/dev/null || true
  fi
  echo -e "${GREEN}✔ Build complete! Output: ${DIST_DIR}/${PROJECT_NAME}${NC}"
}

build_docker() {
  local build_version="${1:-$VERSION}"
  local image_tag="${2:-$PROJECT_NAME}"

  if ! command_exists docker; then
    echo -e "${RED}❌ Error: docker command not found.${NC}"
    exit 1
  fi

  echo -e "${YELLOW}🐳 Building Docker image...${NC}"
  echo -e "${CYAN}   Tag:     ${image_tag}${NC}"
  echo -e "${CYAN}   Version: ${build_version}${NC}"

  docker build --build-arg VERSION="$build_version" -t "$image_tag" .

  echo -e "${GREEN}✔ Docker build complete: ${image_tag}${NC}"
}

zip_dist() {
  local target="${DIST_DIR}/${PROJECT_NAME}"
  [ ! -f "$target" ] && { echo -e "${RED}❌ Binary not found.${NC}"; exit 1; }
  zip -j "${PROJECT_NAME}.zip" "$target"
  echo -e "${GREEN}✔ Created ${PROJECT_NAME}.zip${NC}"
}

generate_checksums() {
  local target="${DIST_DIR}/${PROJECT_NAME}"
  [ ! -f "$target" ] && { echo -e "${RED}❌ Binary not found.${NC}"; exit 1; }
  if command_exists sha256sum; then
    sha256sum "$target" > "${target}.sha256"
  else
    shasum -a 256 "$target" > "${target}.sha256"
  fi
  echo -e "${GREEN}✔ Checksum saved to ${target}.sha256${NC}"
}

clean() {
  echo -e "${YELLOW}🧹 Cleaning artifacts...${NC}"
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