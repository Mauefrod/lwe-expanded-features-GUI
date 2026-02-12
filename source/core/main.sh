#!/bin/bash
set -euo pipefail

# Source utilities
export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/bash_utils.sh"

DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/linux-wallpaper-engine-features"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/linux-wallpaper-engine-features"

LOG_FILE="$DATA_DIR/logs.txt"
PID_FILE="$DATA_DIR/loop.pid"
ENGINE_STATE_FILE="$DATA_DIR/engine_state.json"
PREV_WINDOWS_FILE="$DATA_DIR/prev_windows.txt"

# Set log file for bash_utils functions
export LOG_FILE

# Ensure directories exist
mkdir -p "$DATA_DIR" "$CONFIG_DIR"

# Setup X11 and D-Bus environments
setup_environments

POOL=()
ENGINE=""  # Will be detected at startup
ENGINE_ARGS=()
SOUND_ARGS=()
REMOVE_ABOVE="false"
COMMAND=""
DELAY=""
ACTIVE_WIN=""

log "==================== NEW EXECUTION ===================="

###############################################
#  ENGINE DETECTION (uses centralized utility)
###############################################
# Detect engine at startup using centralized utility
if ! ENGINE=$(detect_engine_binary); then
    log_error "CRITICAL: Cannot proceed without engine binary"
    echo "ERROR: linux-wallpaperengine not found in PATH or common locations" >&2
    echo "" >&2
    echo "Please install linux-wallpaperengine first:" >&2
    echo "  - From source: https://github.com/Acters/linux-wallpaperengine" >&2
    echo "  - Arch Linux (AUR): yay -S linux-wallpaperengine-git" >&2
    echo "" >&2
    echo "Or ensure it's in one of these locations:" >&2
    echo "  - System PATH (/usr/bin, /usr/local/bin, ~/.local/bin)" >&2
    echo "  - ./linux-wallpaperengine/build/linux-wallpaperengine" >&2
    exit 1
fi

log "Using engine: $ENGINE"

###############################################
#  GET ENGINE WINDOWS (wrapper using utility)
###############################################
get_engine_windows() {
    # Use centralized window detection utility
    find_engine_windows
}

save_engine_state() {
    local pid="$1"
    shift
    local -a windows=("$@")
    
    # Save PID for later reference
    echo "$pid" > "$ENGINE_STATE_FILE.pid"
    
    # Save windows for fallback detection (one-per-line)
    printf "%s\n" "${windows[@]}" > "$PREV_WINDOWS_FILE"
    
    log "Engine state saved (PID: $pid, windows: ${windows[*]:-none})"
}


###############################################
#  KILL ENGINE (wrapper using utility)
###############################################
kill_previous_engine() {
    log "Killing previous engine instances"
    
    # Use centralized process killer with automatic signal escalation
    # This tries SIGTERM, then SIGKILL if needed
    kill_by_pattern "linux-wallpaperengine" 3
    sleep 0.5
}


###############################################
#  STOP TOTAL (using utilities with signal escalation)
###############################################
cmd_stop() {
    log "Stopping ALL wallpaper engine processes and loops"

    # Kill engine processes with signal escalation (SIGTERM → SIGKILL)
    kill_process "linux-wallpaperengine" 1
    
    # Kill loop process if exists
    if [[ -f "$PID_FILE" ]]; then
        local loop_pid
        loop_pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
        if [[ -n "$loop_pid" ]]; then
            log "Killing loop process with PID: $loop_pid"
            kill_process "$loop_pid" 2  # 2 second timeout for escalation
        fi
        rm -f "$PID_FILE"
    fi
    
    # Final cleanup: kill any remaining main.sh instances
    kill_by_pattern "bash.*main.sh" 1
    
    # Clear state files
    rm -f "$PREV_WINDOWS_FILE" "$ENGINE_STATE_FILE.pid" 2>/dev/null || true
    
    log "Stop command completed - all processes should be terminated"
}


###############################################
#  WAIT FOR WINDOW (wrapper using utility)
###############################################
wait_for_window() {
    # Delegate to centralized window waiting utility with 10 second timeout
    wait_for_new_window 10 "$@"
}


###############################################
#  APPLY WINDOW FLAGS (simplified using utility)
###############################################
apply_window_flags() {
    local win_id="$1"

    if [[ "$REMOVE_ABOVE" == "false" ]]; then
        log "Skipping window flag modifications"
        return
    fi

    log "Applying window flags to $win_id"
    
    # Use centralized utility for wmctrl flag operations
    apply_wmctrl_flag "$win_id" "remove" "above"
    apply_wmctrl_flag "$win_id" "add" "skip_pager"
    apply_wmctrl_flag "$win_id" "add" "below"

    # Restore focus if we have a previous window
    if [[ -n "$ACTIVE_WIN" ]]; then
        log "Restoring focus to previous window: $ACTIVE_WIN"
        xdotool windowactivate "$ACTIVE_WIN" 2>/dev/null || log_warning "Failed to restore focus"
    fi
}


###############################################
#  APPLY WALLPAPER
# apply_wallpaper launches the wallpaper engine for the given wallpaper path, waits for the newly created window, applies window flags (and optionally restores focus), and closes any previous engine windows while logging progress and errors.
apply_wallpaper() {
    local path="$1"

    log "Applying wallpaper: $path"

    # Guardamos las ventanas actuales del engine ANTES de lanzar el nuevo
    local old_windows=()
    mapfile -t old_windows < <(get_engine_windows)
    log "Old engine windows: ${old_windows[*]:-none}"

    ACTIVE_WIN=$(xdotool getactivewindow 2>/dev/null || echo "")
    log "Active window before launch: ${ACTIVE_WIN:-none}"

    # Construir comando completo con flags de sonido
    local -a full_args=("${ENGINE_ARGS[@]}")
    
    # Añadir flags de sonido si existen
    if [[ ${#SOUND_ARGS[@]} -gt 0 ]]; then
        log "Adding sound flags: ${SOUND_ARGS[*]}"
        full_args+=("${SOUND_ARGS[@]}")
    fi
    
    # Añadir el path del wallpaper al final
    full_args+=("$path")

    # Lanzamos el engine con todos los argumentos
    log "Executing: $ENGINE ${full_args[*]}"
    
    # Handle ENGINE commands that might contain spaces
    if [[ "$ENGINE" == *" "* ]]; then
        # ENGINE contains spaces, execute as shell command
        $ENGINE "${full_args[@]}" &
    else
        # ENGINE is a single binary path
        "$ENGINE" "${full_args[@]}" &
    fi
    
    local new_pid=$!
    log "Engine launched with PID $new_pid"
    
    # Start background monitor to continuously try to apply window flags
    if [[ "$REMOVE_ABOVE" == "true" ]]; then
        local monitor_script
        monitor_script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/window-monitor.sh"
        if [[ -f "$monitor_script" ]]; then
            log "Starting background window monitor (REMOVE_ABOVE=true)"
            bash "$monitor_script" "$new_pid" "$REMOVE_ABOVE" "$LOG_FILE" &
            local monitor_pid=$!
            log "Window monitor started with PID $monitor_pid"
        else
            log "WARNING: window-monitor.sh not found at $monitor_script"
        fi
    fi

    # Esperamos a que la NUEVA ventana esté lista (excluyendo las antiguas)
    local win_id
    win_id=$(wait_for_window "${old_windows[@]}")

    if [[ -z "$win_id" ]]; then
        log "ERROR: No window found for new engine"
        return
    fi

    apply_window_flags "$win_id"
    
    # Save current windows for next invocation
    save_engine_state "$new_pid" "$win_id"

    log "New window ready, now killing old instances"
    if [[ ${#old_windows[@]} -gt 0 ]]; then
        for old_win in "${old_windows[@]}"; do
            if [[ "$old_win" != "$win_id" ]]; then
                log "Killing old window: $old_win"
                wmctrl -i -c "$old_win" 2>/dev/null || true
            else
                log "Skipping new window: $old_win (matches $win_id)"
            fi
        done
    else
        log "No old windows to close"
    fi
    
    log "Transition complete"
}


###############################################
#  RANDOM
###############################################
cmd_random() {
    local list=()

    if [[ ${#POOL[@]} -gt 0 ]]; then
        list=("${POOL[@]}")
        log "Using POOL for random selection (${#POOL[@]} items)"
    else
        if [[ -z "${WALLPAPERS_DIRECTORY:-}" ]]; then
            log "ERROR: WALLPAPERS_DIRECTORY is not set"
            return
        fi
        log "POOL empty, scanning directory: $WALLPAPERS_DIRECTORY"
        mapfile -t list < <(find "$WALLPAPERS_DIRECTORY" -mindepth 1 -maxdepth 1 -type d)
    fi

    if [[ ${#list[@]} -eq 0 ]]; then
        log "ERROR: No wallpapers found for random selection"
        return
    fi

    local id="${list[RANDOM % ${#list[@]}]}"
    log "Randomly selected: $id"
    apply_wallpaper "$id"
}


###############################################
#  SET
###############################################
cmd_set() {
    log "Setting wallpaper (set): $1"
    apply_wallpaper "$1"
}


###############################################
#  LIST
###############################################
cmd_list() {
    if [[ -z "${WALLPAPERS_DIRECTORY:-}" ]]; then
        log "ERROR: WALLPAPERS_DIRECTORY is not set for list"
        return
    fi
    log "Listing wallpapers in: $WALLPAPERS_DIRECTORY"
    mapfile -t WALLPAPERS_IDS < <(find "$WALLPAPERS_DIRECTORY" -mindepth 1 -maxdepth 1 -type d)
    printf "%s\n" "${WALLPAPERS_IDS[@]}"
}


###############################################
#  AUTO RANDOM LOOP
###############################################
cmd_auto_random() {
    log "Starting auto-random mode with delay: $DELAY seconds"
    # Guardar el PID del loop actual
    echo $$ > "$PID_FILE"
    trap 'kill_previous_engine' EXIT

    while true; do
        cmd_random
        sleep "$DELAY"
    done
}


###############################################
#  PARSER DE ARGUMENTOS
###############################################
log "Parsing arguments: $*"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir)
            WALLPAPERS_DIRECTORY="$2"
            log "Directory set to: $WALLPAPERS_DIRECTORY"
            shift 2
            ;;
        --set)
            COMMAND="set"
            ARGUMENTS="$2"
            log "Command: set ($ARGUMENTS)"
            shift 2
            ;;
        --random)
            COMMAND="random"
            log "Command: random"
            shift
            ;;
        --list)
            COMMAND="list"
            log "Command: list"
            shift
            ;;
        --delay)
            COMMAND="auto-random"
            DELAY="$2"
            log "Command: auto-random, delay=$DELAY"
            shift 2
            ;;
        --above)
            REMOVE_ABOVE="true"
            log "Flag: remove above priority"
            shift
            ;;
        --pool)
            log "Reading POOL items..."
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                log "POOL += $1"
                POOL+=("$1")
                shift
            done
            ;;
        --sound)
            log "Reading SOUND flags..."
            shift
            # Leer todos los flags de sonido hasta encontrar otro flag principal (--) o fin de argumentos
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --silent)
                        SOUND_ARGS+=("--silent")
                        log "SOUND_FLAG: --silent (mute background audio)"
                        shift
                        ;;
                    --volume)
                        if [[ $# -lt 2 ]]; then
                            log "ERROR: --volume requires a value"
                            shift
                            break
                        fi
                        SOUND_ARGS+=("--volume" "$2")
                        log "SOUND_FLAG: --volume $2"
                        shift 2
                        ;;
                    --noautomute)
                        SOUND_ARGS+=("--noautomute")
                        log "SOUND_FLAG: --noautomute (don't mute when other apps play audio)"
                        shift
                        ;;
                    --no-audio-processing)
                        SOUND_ARGS+=("--no-audio-processing")
                        log "SOUND_FLAG: --no-audio-processing (disable audio reactive features)"
                        shift
                        ;;
                    --*)
                        # Encontramos otro flag principal, salir del loop de sonido
                        log "End of sound flags, found: $1"
                        break
                        ;;
                    *)
                        log "WARNING: Unknown sound flag: $1 (ignoring)"
                        shift
                        ;;
                esac
            done
            ;;
        --stop)
            COMMAND="stop"
            log "Command: stop"
            shift
            ;;
        *)
            ENGINE_ARGS+=("$1")
            log "ENGINE_ARG += $1"
            shift
            ;;
    esac
done


###############################################
#  EJECUCIÓN
###############################################
log "Executing command: $COMMAND"

case "$COMMAND" in
    random) cmd_random ;;
    set) cmd_set "$ARGUMENTS" ;;
    list) cmd_list ;;
    auto-random) cmd_auto_random ;;
    stop) cmd_stop ;;
    *)
        log "ERROR: No command specified"
        echo "No command specified"
        exit 1
        ;;
esac
