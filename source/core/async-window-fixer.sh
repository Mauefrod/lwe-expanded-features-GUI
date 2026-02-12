#!/bin/bash
# async-window-fixer.sh - Asynchronous window flag manipulation utility
# Launches completely non-blocking window manipulation attempts in background

set -euo pipefail

# Source utilities
export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/bash_utils.sh"

ENGINE_PID="${1:-}"

if [[ -z "$ENGINE_PID" ]]; then
    log_error "Missing ENGINE_PID argument"
    exit 1
fi

log_debug "Async window fixer launched for PID $ENGINE_PID"

# Apply background processing flags to all engine windows
{
    if local -a windows=(); mapfile -t windows < <(find_engine_windows); [[ ${#windows[@]} -gt 0 ]]; then
        apply_flags_to_windows "${windows[@]}"
    fi
} &

# Return immediately without waiting
exit 0
