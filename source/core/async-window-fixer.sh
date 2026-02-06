#!/bin/bash
# async-window-fixer.sh
# Asynchronous window flag manipulation
# Launches window manipulation attempts in completely non-blocking way

set -euo pipefail

ENGINE_PID="${1:-}"

if [[ -z "$ENGINE_PID" ]]; then
    exit 1
fi

# Apply window flags in non-blocking way
apply_flags() {
    local pid=$1
    # Timeout after 2 seconds, run in background, suppress all output
    timeout 2 wmctrl -lx 2>/dev/null | grep -i "linux-wallpaperengine\|wallpaperengine\|steam_app_431960" | awk '{print $1}' | while read -r win; do
        timeout 1 wmctrl -i -r "$win" -b remove,above 2>/dev/null || true &
        timeout 1 wmctrl -i -r "$win" -b add,skip_pager 2>/dev/null || true &
        timeout 1 wmctrl -i -r "$win" -b add,below 2>/dev/null || true &
    done &
}

apply_flags "$ENGINE_PID" &

# Return immediately, don't wait for background jobs
exit 0
