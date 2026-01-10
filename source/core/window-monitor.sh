#!/bin/bash
# window-monitor.sh
# Background daemon to monitor and manipulate LWE windows
# This script runs in the background and periodically attempts to apply window flags
# even when wmctrl is restricted in Flatpak, it acts as a persistent watcher/manipulator
#
# Usage: window-monitor.sh <pid> <remove_above> [log_file]
# Args:
#   pid: PID of the engine process to monitor
#   remove_above: "true" or "false" - whether to remove above flag
#   log_file: optional log file path

set -euo pipefail

ENGINE_PID="${1:-}"
REMOVE_ABOVE="${2:-false}"
LOG_FILE="${3:-}"

# Exit if no PID provided
if [[ -z "$ENGINE_PID" ]]; then
    exit 1
fi

# Logging function
log_monitor() {
    if [[ -n "$LOG_FILE" ]] && [[ -w "$LOG_FILE" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [MONITOR-$$] $*" >> "$LOG_FILE"
    fi
}

log_monitor "Starting window monitor for PID $ENGINE_PID (remove_above=$REMOVE_ABOVE)"

# Counter for retry attempts
attempt=0
max_attempts=600  # 5 minutes with 0.5s intervals

while [[ $attempt -lt $max_attempts ]]; do
    # Check if engine process is still alive
    if ! kill -0 "$ENGINE_PID" 2>/dev/null; then
        log_monitor "Engine PID $ENGINE_PID is no longer running, exiting monitor"
        exit 0
    fi
    
    attempt=$((attempt + 1))
    
    # Try to find and manipulate windows
    if command -v wmctrl >/dev/null 2>&1; then
        # Try wmctrl to list and manipulate windows
        local -a windows
        mapfile -t windows < <(wmctrl -lx 2>/dev/null | grep -i "linux-wallpaperengine\|wallpaperengine\|steam_app_431960" | awk '{print $1}' || true)
        
        if [[ ${#windows[@]} -gt 0 ]]; then
            for win in "${windows[@]}"; do
                if [[ -n "$win" ]]; then
                    if [[ "$REMOVE_ABOVE" == "true" ]]; then
                        # Try to remove above flag and add below
                        wmctrl -i -r "$win" -b remove,above 2>/dev/null || true
                        wmctrl -i -r "$win" -b add,skip_pager 2>/dev/null || true
                        wmctrl -i -r "$win" -b add,below 2>/dev/null || true
                        if [[ $((attempt % 20)) -eq 0 ]]; then
                            log_monitor "Applied window flags to window $win (attempt $attempt)"
                        fi
                    fi
                fi
            done
        fi
    fi
    
    # Sleep briefly before next attempt
    sleep 0.5
done

log_monitor "Monitor exceeded max attempts ($max_attempts), exiting"
exit 0
