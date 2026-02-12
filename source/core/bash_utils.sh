#!/bin/bash
# bash_utils.sh - Common utilities for LWE bash scripts
# Centralizes logging, process management, window manipulation, and error handling
# Source this file in your script: source bash_utils.sh

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

export DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/linux-wallpaper-engine-features"
export CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/linux-wallpaper-engine-features"
export LOG_FILE="${LOG_FILE:-$DATA_DIR/logs.txt}"

# Ensure directories exist
mkdir -p "$DATA_DIR" "$CONFIG_DIR"

# =============================================================================
# LOGGING UTILITIES
# =============================================================================

# Generic logging function with timestamp
log_to_file() {
    local msg="$1"
    local level="${2:-INFO}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    local formatted="[$timestamp] [$level] $msg"
    echo "$formatted" >> "$LOG_FILE"
}

# Backward compatible alias for existing scripts
log() {
    log_to_file "$1" "INFO"
}

# Log with specific levels
log_error() {
    log_to_file "$1" "ERROR"
}

log_warning() {
    log_to_file "$1" "WARNING"
}

log_debug() {
    log_to_file "$1" "DEBUG"
}

log_success() {
    log_to_file "$1" "SUCCESS"
}

# =============================================================================
# WINDOW DETECTION UTILITIES
# =============================================================================

# Search for engine windows using multiple strategies
find_engine_windows() {
    local -a windows=()
    
    # Strategy 1: Use wmctrl (most reliable if available)
    if command -v wmctrl &>/dev/null; then
        mapfile -t windows < <(wmctrl -lx 2>/dev/null | \
            grep -iE "linux-wallpaperengine|wallpaperengine|steam_app_431960" | \
            awk '{print $1}' || true)
        
        if [[ ${#windows[@]} -gt 0 ]]; then
            printf '%s\n' "${windows[@]}"
            return 0
        fi
    fi
    
    # Strategy 2: Use xdotool (fallback) - match only actual engine windows, not GUI
    # Explicitly check window names to exclude GUI window
    if command -v xdotool &>/dev/null; then
        mapfile -t windows < <(xdotool search --name "wallpaper" 2>/dev/null | \
            while read -r win_id; do
                win_title=$(xdotool getwindowname "$win_id" 2>/dev/null || echo "")
                # Exclude GUI windows
                if [[ ! "$win_title" =~ "GUI" ]]; then
                    echo "$win_id"
                fi
            done || true)
        
        if [[ ${#windows[@]} -gt 0 ]]; then
            printf '%s\n' "${windows[@]}"
            return 0
        fi
    fi
    
    return 1
}

# Get all engine windows (returns array-compatible format)
get_engine_windows() {
    find_engine_windows || echo ""
}

# Find window for specific PID
find_window_for_pid() {
    local pid="$1"
    local max_attempts="${2:-5}"
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        # Try wmctrl with PID
        if command -v wmctrl &>/dev/null; then
            local win_id
            win_id=$(wmctrl -lp 2>/dev/null | awk -v p="$pid" '$3 == p {print $1; exit}' || true)
            if [[ -n "$win_id" ]]; then
                echo "$win_id"
                return 0
            fi
        fi
        
        # Try xdotool
        if command -v xdotool &>/dev/null; then
            local win_id
            win_id=$(xdotool search --pid "$pid" 2>/dev/null | head -1 || true)
            if [[ -n "$win_id" ]]; then
                echo "$win_id"
                return 0
            fi
        fi
        
        attempt=$((attempt + 1))
        [[ $attempt -lt $max_attempts ]] && sleep 0.2
    done
    
    return 1
}

# =============================================================================
# WINDOW MANIPULATION UTILITIES
# =============================================================================

# Generic helper to apply wmctrl flags
apply_wmctrl_flag() {
    local win_id="$1"
    local operation="$2"  # "add" or "remove"
    local flag="$3"       # "above", "below", "skip_pager", etc.
    
    if ! command -v wmctrl &>/dev/null; then
        log_warning "wmctrl not available, cannot apply flag: $flag"
        return 1
    fi
    
    if wmctrl -i -r "$win_id" -b "$operation","$flag" 2>/dev/null; then
        log_debug "Applied wmctrl flag: $operation $flag to $win_id"
        return 0
    else
        log_warning "Failed to apply wmctrl flag: $operation $flag to $win_id"
        return 1
    fi
}

# Remove above flag and add below/skip_pager (common operation)
apply_background_flags() {
    local win_id="$1"
    
    apply_wmctrl_flag "$win_id" "remove" "above" || true
    apply_wmctrl_flag "$win_id" "add" "skip_pager" || true
    apply_wmctrl_flag "$win_id" "add" "below" || true
}

# Close window gracefully
close_window() {
    local win_id="$1"
    
    if ! command -v wmctrl &>/dev/null; then
        log_warning "wmctrl not available, cannot close window: $win_id"
        return 1
    fi
    
    if wmctrl -i -c "$win_id" 2>/dev/null; then
        log_debug "Closed window: $win_id"
        return 0
    else
        log_warning "Failed to close window: $win_id"
        return 1
    fi
}

# Manipulate multiple windows
apply_flags_to_windows() {
    local -a windows=("$@")
    local success_count=0
    local total_count=${#windows[@]}
    
    for win in "${windows[@]}"; do
        if [[ -n "$win" ]]; then
            apply_background_flags "$win" && ((success_count++)) || true
        fi
    done
    
    log_debug "Applied flags to $success_count/$total_count windows"
    return $([[ $success_count -gt 0 ]])
}

# =============================================================================
# PROCESS MANAGEMENT UTILITIES
# =============================================================================

# Check if process is running
is_process_running() {
    local pid="${1:-}"
    
    if [[ -z "$pid" ]]; then
        return 1
    fi
    
    kill -0 "$pid" 2>/dev/null || return 1
}

# Kill process gracefully with fallback to SIGKILL
kill_process() {
    local pid="$1"
    local signal="TERM"
    local max_attempts=3
    local attempt=0
    
    if ! is_process_running "$pid"; then
        log_debug "Process $pid not running"
        return 0
    fi
    
    while [[ $attempt -lt $max_attempts ]]; do
        kill -"$signal" "$pid" 2>/dev/null || true
        sleep 0.3
        
        if ! is_process_running "$pid"; then
            log_debug "Process $pid killed with SIG$signal"
            return 0
        fi
        
        signal="KILL"
        attempt=$((attempt + 1))
    done
    
    log_error "Failed to kill process $pid after $max_attempts attempts"
    return 1
}

# Kill all processes matching pattern
kill_by_pattern() {
    local pattern="$1"
    local signal="${2:-TERM}"
    
    log_debug "Killing processes matching: $pattern (signal: SIG$signal)"
    pkill -"$signal" -f "$pattern" 2>/dev/null || true
}

# =============================================================================
# ENGINE DETECTION UTILITIES
# =============================================================================

# Detect engine binary in PATH and common locations
detect_engine_binary() {
    local engine_path=""
    
    # Check PATH first
    for binary in linux-wallpaperengine wallpaperengine; do
        if command -v "$binary" &>/dev/null; then
            engine_path="$binary"
            log_success "Engine found in PATH: $engine_path"
            echo "$engine_path"
            return 0
        fi
    done
    
    # Get the script directory (relative path checking)
    local script_dir="${SCRIPT_DIR:-.}"
    
    # Check common installation locations
    local -a locations=(
        "$HOME/.local/bin/linux-wallpaperengine"
        "/usr/local/bin/linux-wallpaperengine"
        "/usr/bin/linux-wallpaperengine"
        "$HOME/linux-wallpaperengine/build/output/linux-wallpaperengine"
        "$HOME/linux-wallpaperengine/build/linux-wallpaperengine"
        "$script_dir/../../linux-wallpaperengine/build/output/linux-wallpaperengine"
        "$script_dir/../../linux-wallpaperengine/build/linux-wallpaperengine"
        "$script_dir/../linux-wallpaperengine/build/output/linux-wallpaperengine"
        "$script_dir/../linux-wallpaperengine/build/linux-wallpaperengine"
    )
    
    for location in "${locations[@]}"; do
        if [[ -x "$location" ]]; then
            # Resolve to absolute path
            location="$(cd "$(dirname "$location")" 2>/dev/null && pwd)/$(basename "$location")"
            engine_path="$location"
            log_success "Engine found at: $engine_path"
            # Add to PATH for this session
            local bin_dir
            bin_dir=$(dirname "$location")
            export PATH="$bin_dir:$PATH"
            echo "$engine_path"
            return 0
        fi
    done
    
    log_error "Engine not found in PATH or common locations"
    return 1
}

# =============================================================================
# ENVIRONMENT SETUP UTILITIES
# =============================================================================

# Setup X11 environment variables
setup_x11_environment() {
    # Set DISPLAY if not already set
    if [[ -z "$DISPLAY" ]]; then
        # Try to extract from running processes
        for pid in $(pgrep -u "$UID" -f "^/usr/bin/X|^/usr/bin/Xvfb" 2>/dev/null || true); do
            export DISPLAY=$(grep -z ^DISPLAY= "/proc/$pid/environ" 2>/dev/null | sed 's/DISPLAY=//' || true)
            [[ -n "$DISPLAY" ]] && break
        done
        
        # Fallback
        export DISPLAY="${DISPLAY:-:0}"
    fi
    
    log_debug "DISPLAY=$DISPLAY"
    
    # Set XAUTHORITY if not set
    if [[ -z "$XAUTHORITY" ]]; then
        for pid in $(pgrep -u "$UID" 2>/dev/null | head -5); do
            local xauth_path
            xauth_path=$(grep -z ^XAUTHORITY= "/proc/$pid/environ" 2>/dev/null | sed 's/XAUTHORITY=//' || true)
            if [[ -n "$xauth_path" ]] && [[ -f "$xauth_path" ]]; then
                export XAUTHORITY="$xauth_path"
                break
            fi
        done
        
        export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"
    fi
    
    log_debug "XAUTHORITY=$XAUTHORITY"
}

# Setup D-Bus environment
setup_dbus_environment() {
    if [[ -z "$DBUS_SESSION_BUS_ADDRESS" ]]; then
        local bus_path="/run/user/$(id -u)/bus"
        if [[ -f "$bus_path" ]]; then
            export DBUS_SESSION_BUS_ADDRESS="unix:path=$bus_path"
            log_debug "Set DBUS_SESSION_BUS_ADDRESS"
        fi
    fi
}

# Setup all environments
setup_environments() {
    setup_x11_environment
    setup_dbus_environment
    
    log_debug "Environment setup complete"
}

# =============================================================================
# FILE MANAGEMENT UTILITIES
# =============================================================================

# Safely read JSON value (simple bash without jq)
json_get_value() {
    local file="$1"
    local key="$2"
    
    grep -o "\"$key\": [^,}]*" "$file" 2>/dev/null | cut -d: -f2 | xargs || echo ""
}

# Escape string for JSON
json_escape() {
    local str="$1"
    str="${str//\\/\\\\}"  # Escape backslashes
    str="${str//\"/\\\"}"  # Escape quotes
    printf '%s' "$str"
}

# Cleanup old log files
cleanup_old_logs() {
    local max_age_days="${1:-7}"
    local max_age_seconds=$((max_age_days * 86400))
    local now=$(date +%s)
    
    if [[ -f "$LOG_FILE" ]]; then
        local file_age=$((now - $(stat -c%Y "$LOG_FILE" 2>/dev/null || echo 0)))
        if [[ $file_age -gt $max_age_seconds ]]; then
            rm -f "$LOG_FILE"
            log_success "Cleaned up old log file"
        fi
    fi
}

# =============================================================================
# X11 UTILITIES
# =============================================================================

# Force X11 server to sync
sync_x11() {
    if command -v xdotool &>/dev/null; then
        timeout 1 xdotool getactivewindow >/dev/null 2>&1 || true
    fi
    sleep 0.1
}

# Get active window ID
get_active_window() {
    if command -v xdotool &>/dev/null; then
        xdotool getactivewindow 2>/dev/null || echo ""
    fi
}

# Restore window focus
restore_window_focus() {
    local win_id="${1:-}"
    
    if [[ -z "$win_id" ]]; then
        return 1
    fi
    
    if command -v xdotool &>/dev/null; then
        if xdotool windowactivate "$win_id" 2>/dev/null; then
            log_debug "Restored focus to window: $win_id"
            return 0
        fi
    fi
    
    return 1
}

# =============================================================================
# WAIT UTILITIES
# =============================================================================

# Wait for new window to appear (excluding known windows)
wait_for_new_window() {
    local -a exclude_windows=("$@")
    local max_attempts=200
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        local -a current_windows=()
        mapfile -t current_windows < <(find_engine_windows)
        
        # Look for window not in exclusion list
        for w in "${current_windows[@]}"; do
            local is_known=false
            for excl_w in "${exclude_windows[@]}"; do
                if [[ "$w" == "$excl_w" ]]; then
                    is_known=true
                    break
                fi
            done
            
            if [[ "$is_known" == "false" ]]; then
                log_success "New window detected: $w"
                echo "$w"
                return 0
            fi
        done
        
        attempt=$((attempt + 1))
        sleep 0.05
    done
    
    log_error "Timeout waiting for new window"
    return 1
}
