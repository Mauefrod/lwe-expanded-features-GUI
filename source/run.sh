#!/bin/bash
set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$SCRIPT_DIR/source/core"
source "$CORE_DIR/bash_utils.sh"

# Color codes (for backward compatibility with existing output)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the root directory of the project
ROOT_DIR="$SCRIPT_DIR"

# Check if virtual environment exists (warning only)
if [[ ! -d "$ROOT_DIR/.venv" ]]; then
    echo -e "${YELLOW}[i]${NC} Virtual environment not found at $ROOT_DIR/.venv"
    log_warning "Virtual environment not found - will use system python"
fi

# Setup virtual environment or use system python
VENV_PATH="$ROOT_DIR/.venv"
if [[ -f "$VENV_PATH/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$VENV_PATH/bin/activate"
    VENV_PY="$VENV_PATH/bin/python"
    echo -e "${YELLOW}[i]${NC} Activated virtualenv: $VENV_PATH"
    log_success "Virtual environment activated"
else
    echo -e "${YELLOW}[i]${NC} Virtualenv not found, will try system python3"
    log_warning "Virtualenv not found, using system python"
    VENV_PY="$(command -v python3 || true)"
    if [[ -z "$VENV_PY" ]]; then
        echo -e "${RED}[✗]${NC} python3 not found on PATH"
        log_error "Python3 not found"
        exit 1
    fi
fi

# Detect backend engine
if ! BACKEND_PATH=$(detect_engine_binary); then
    echo -e "${RED}[✗]${NC} linux-wallpaperengine not found"
    log_error "Backend detection failed"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} Backend found: $BACKEND_PATH"

# Change to source directory
cd "$SCRIPT_DIR/source"

# Ensure GUI entry point exists
if [[ ! -f "GUI.py" ]]; then
    echo -e "${RED}[✗]${NC} GUI.py not found in $PWD"
    log_error "GUI.py not found"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} Starting GUI..."
log_success "Launching GUI"

# Run the GUI application
"$VENV_PY" GUI.py
    exit 1
fi

# Trap to ensure we attempt to deactivate virtualenv on exit
trap 'deactivate 2>/dev/null || true' EXIT

# Run the application (use venv python explicitly)
echo -e "${GREEN}[✓]${NC} Starting Linux Wallpaper Engine GUI..."
PYTHONUNBUFFERED=1 "$VENV_PY" GUI.py "$@"
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    echo -e "${RED}[✗]${NC} GUI exited with code $EXIT_CODE"
else
    echo -e "${GREEN}[✓]${NC} GUI exited successfully"
fi

exit $EXIT_CODE
