#!/bin/bash
# window-monitor.sh - Background daemon to monitor and manipulate wallpaper engine windows
# Uses window utilities to detect and apply flags asynchronously
# Usage: window-monitor.sh <pid> <remove_above> [log_file]

set -euo pipefail

# Source utilities
export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/bash_utils.sh"

ENGINE_PID="${1:-}"
REMOVE_ABOVE="${2:-false}"

if [[ -z "$ENGINE_PID" ]]; then
    log_error "Missing ENGINE_PID argument"
    exit 1
fi

log_debug "Starting window monitor for PID $ENGINE_PID (REMOVE_ABOVE=$REMOVE_ABOVE)"

attempt=0
max_attempts=600  # 5 minutes at 0.5 second intervals
window_found=false

while [[ $attempt -lt $max_attempts ]]; do
    # Check if engine process is still alive
    if ! is_process_running "$ENGINE_PID"; then
        log_debug "Engine PID $ENGINE_PID died, exiting monitor"
        exit 0
    fi
    
    attempt=$((attempt + 1))
    
    if [[ "$REMOVE_ABOVE" == "true" ]]; then
        # Try to find window by PID and apply flags
        if ! $window_found; then
            if win_id=$(find_window_for_pid "$ENGINE_PID" 1); then
                log_success "Found window $win_id for PID $ENGINE_PID"
                window_found=true
                apply_background_flags "$win_id" &
            fi
        fi
        
        # Also try generic window search (fallback)
        local -a current_windows=()
        mapfile -t current_windows < <(find_engine_windows || true)
        if [[ ${#current_windows[@]} -gt 0 ]]; then
            apply_flags_to_windows "${current_windows[@]}" >/dev/null 2>&1 &
        fi
        
        # Log periodic status
        if [[ $((attempt % 60)) -eq 0 ]]; then
            log_debug "Monitor running - attempt $attempt/$max_attempts (window_found: $window_found)"
        fi
    fi
    
    sleep 0.5
done

log_warning "Monitor exceeded max attempts ($max_attempts), exiting"
exit 0