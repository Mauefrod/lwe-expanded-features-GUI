#!/bin/bash
# lwe-state-manager.sh - Engine state management helper script
# Tracks and manages engine state for better process tracking and recovery

set -euo pipefail

# Source utilities
export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/bash_utils.sh"

# Configuration
ENGINE_STATE="$DATA_DIR/engine.state"
ENGINES_RUNNING="$DATA_DIR/engines_running"

# Initialize empty state if missing
init_state() {
    if [[ ! -f "$ENGINE_STATE" ]]; then
        cat > "$ENGINE_STATE" <<EOF
{
  "last_pid": null,
  "last_windows": [],
  "last_wallpaper": null,
  "last_execution": null
}
EOF
        log_success "Initialized state file: $ENGINE_STATE"
    fi
}

# Save current engine state
save_state() {
    local pid="$1"
    local windows="${2:-}"
    local wallpaper="${3:-}"
    
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local escaped_wallpaper
    escaped_wallpaper=$(json_escape "$wallpaper")
    
    # Simple JSON write (bash-only, no jq dependency)
    cat > "$ENGINE_STATE" <<EOF
{
  "last_pid": $pid,
  "last_windows": [$(printf '"%s"' "${windows:-}")],
  "last_wallpaper": "$escaped_wallpaper",
  "last_execution": "$timestamp"
}
EOF
    
    log_debug "State saved: PID=$pid, Windows=${windows:-none}"
}

# Get last engine PID
get_last_pid() {
    init_state
    json_get_value "$ENGINE_STATE" "last_pid" || echo ""
}

# Get last engine windows
get_last_windows() {
    init_state
    
    if grep -q '"last_windows": \[\]' "$ENGINE_STATE"; then
        echo ""
    else
        # Extract window IDs (simple regex, assumes hex format 0xNNNNNNNN)
        grep -o '0x[0-9a-f]*' "$ENGINE_STATE" || true
    fi
}

# Check if a process is still running (uses utility function)
check_running() {
    local pid="$1"
    
    if is_process_running "$pid"; then
        echo "yes"
    else
        echo "no"
    fi
}

# Kill engine by PID with fallback
kill_engine() {
    local pid="${1:-}"
    
    log_debug "Killing engine (PID: ${pid:-unknown})"
    
    if [[ -n "$pid" ]] && is_process_running "$pid"; then
        kill_process "$pid"
    fi
    
    # Fallback: kill by pattern
    kill_by_pattern "linux-wallpaperengine" "KILL"
    
    # Clear state
    save_state "null" "" ""
    log_success "Engine killed and state cleared"
}

# Monitor and track engines
track_engine() {
    local pid="$1"
    local wallpaper="${2:-}"
    
    # Save state
    save_state "$pid" "" "$wallpaper"
    
    # Add to running engines list
    echo "$pid:$wallpaper:$(date +%s)" >> "$ENGINES_RUNNING"
    
    # Cleanup old entries (keep only last 100)
    if [[ $(wc -l < "$ENGINES_RUNNING") -gt 100 ]]; then
        tail -100 "$ENGINES_RUNNING" > "$ENGINES_RUNNING.tmp"
        mv "$ENGINES_RUNNING.tmp" "$ENGINES_RUNNING"
    fi
    
    log_debug "Tracked engine: PID=$pid, Wallpaper=$wallpaper"
}

# Print state info for debugging
show_state() {
    echo "=== LWE Engine State ==="
    echo "State File: $ENGINE_STATE"
    
    if [[ -f "$ENGINE_STATE" ]]; then
        cat "$ENGINE_STATE"
    else
        echo "No state file found"
    fi
    
    echo ""
    echo "Last PID: $(get_last_pid)"
    echo "Last Windows: $(get_last_windows)"
    
    if [[ -f "$ENGINES_RUNNING" ]]; then
        echo ""
        echo "Recent Engines (last 10):"
        tail -10 "$ENGINES_RUNNING"
    fi
}

# Cleanup old state files
cleanup() {
    cleanup_old_logs 7
    
    if [[ -f "$ENGINES_RUNNING" ]]; then
        # Keep only last 50 entries
        if [[ $(wc -l < "$ENGINES_RUNNING") -gt 50 ]]; then
            tail -50 "$ENGINES_RUNNING" > "$ENGINES_RUNNING.tmp"
            mv "$ENGINES_RUNNING.tmp" "$ENGINES_RUNNING"
        fi
        log_debug "Cleaned up engines_running file"
    fi
}

# Main command handling
case "${1:-help}" in
    init)
        init_state
        ;;
    save)
        save_state "$2" "${3:-}" "${4:-}"
        ;;
    get-pid)
        get_last_pid
        ;;
    get-windows)
        get_last_windows
        ;;
    is-running)
        check_running "$2"
        ;;
    kill)
        kill_engine "${2:-}"
        ;;
    track)
        track_engine "$2" "${3:-}"
        ;;
    show)
        show_state
        ;;
    cleanup)
        cleanup
        ;;
    *)
        echo "Usage: lwe-state-manager.sh {init|save|get-pid|get-windows|is-running|kill|track|show|cleanup}"
        exit 1
        ;;
esac    help|*)
        cat <<EOF
LWE State Manager - Manage linux-wallpaperengine state

Usage: $0 COMMAND [ARGS]

Commands:
    init                 Initialize state file
    save PID WINDOWS WP   Save engine state
    get-pid              Get last engine PID
    get-windows          Get last engine windows
    is-running PID       Check if PID is running
    kill [PID]          Kill engine (by PID or process name)
    track PID [WP]      Track new engine execution
    show                 Display current state
    cleanup              Clean up old state files
    help                 Show this help message

Environment:
    STATE_DIR: $STATE_DIR
    ENGINE_STATE: $ENGINE_STATE
    ENGINES_RUNNING: $ENGINES_RUNNING

Example:
    $0 track 12345 /path/to/wallpaper
    $0 show
    $0 kill

EOF
        ;;
esac
