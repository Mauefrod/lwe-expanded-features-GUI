#!/bin/bash
# Wrapper script for Linux Wallpaper Engine GUI Flatpak
# This ensures proper directory setup and environment configuration

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Flatpak application directory
APP_DIR="/app/share/lwe-gui"
SOURCE_DIR="$APP_DIR/source"

# Use XDG base directories (Flatpak best practice)
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/linux-wallpaper-engine-features"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/linux-wallpaper-engine-features"

# Create necessary directories
mkdir -p "$CONFIG_DIR" "$DATA_DIR"

# Export environment variables for the backend script to use
export LWE_DATA_DIR="$DATA_DIR"
export LWE_CONFIG_DIR="$CONFIG_DIR"
export LWE_BACKEND_SCRIPT="$SOURCE_DIR/core/main.sh"

# Verify linux-wallpaperengine is available
if ! command -v linux-wallpaperengine >/dev/null 2>&1; then
    echo -e "${RED}ERROR:${NC} linux-wallpaperengine binary not found in Flatpak"
    echo -e "${YELLOW}The application may not function correctly${NC}"
    echo ""
fi

# Verify backend script exists
if [[ ! -f "$SOURCE_DIR/core/main.sh" ]]; then
    echo -e "${RED}ERROR:${NC} Backend script not found at $SOURCE_DIR/core/main.sh"
    echo -e "${YELLOW}The application will not be able to manage wallpapers${NC}"
    echo ""
fi

# Ensure backend script is executable
if [[ -f "$SOURCE_DIR/core/main.sh" ]]; then
    chmod +x "$SOURCE_DIR/core/main.sh" 2>/dev/null || true
fi

# Change to source directory where GUI.py is located
cd "$SOURCE_DIR" || {
    echo -e "${RED}ERROR:${NC} Cannot change to source directory: $SOURCE_DIR"
    exit 1
}

# Verify GUI.py exists
if [[ ! -f "GUI.py" ]]; then
    echo -e "${RED}ERROR:${NC} GUI.py not found in $SOURCE_DIR"
    exit 1
fi

# Run the GUI application
exec python3 GUI.py "$@"