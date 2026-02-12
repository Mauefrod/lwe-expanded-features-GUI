#!/bin/bash
# startup_handler.sh - Systemd startup handler for Linux Wallpaper Engine
# Executed by systemd at user login to start wallpaper engine with saved config
# Called by: systemd (linux-wallpaperengine.service)

set -e

# Source utilities
export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/bash_utils.sh"

log_success "========== Startup Handler Started =========="
log_debug "Script directory: $SCRIPT_DIR"
log_debug "User: $(id -un) (UID: $(id -u))"
log_debug "Home: $HOME"

# Setup complete environment before Python execution
setup_environments

log_debug "Environment setup complete"

# Change to script directory for proper imports
cd "$SCRIPT_DIR" || {
    log_error "Failed to change to script directory: $SCRIPT_DIR"
    exit 1
}

log_debug "Working directory: $(pwd)"

# Verify Python is available
if ! command -v python3 &> /dev/null; then
    log_error "python3 not found in PATH"
    exit 1
fi

log_debug "Python: $(python3 --version)"

# Execute startup manager
if ! python3 << 'PYTHON_EOF'
import sys
import traceback
from pathlib import Path

try:
    script_dir = '$SCRIPT_DIR'
    source_dir = str(Path(script_dir).parent)
    
    sys.path.insert(0, source_dir)
    sys.path.insert(0, script_dir)
    
    from startup_manager import run_at_startup
    run_at_startup()
    
except ImportError as e:
    print(f"[ERROR] Failed to import startup_manager: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF
then
    log_error "Python execution failed with exit code $?"
    exit 1
fi

log_success "========== Startup Handler Completed Successfully =========="
exit 0