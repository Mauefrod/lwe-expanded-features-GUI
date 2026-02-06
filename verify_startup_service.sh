#!/bin/bash
# ==============================================================================
# Linux Wallpaper Engine - Startup Service Verification Script
# ==============================================================================
# This script verifies that the startup service is properly configured and
# working. Run this regularly to ensure everything is functioning correctly.
#
# Usage: bash verify_startup_service.sh
# ==============================================================================

COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_RESET='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
pass() {
    echo -e "${COLOR_GREEN}✓ PASS${COLOR_RESET}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${COLOR_RED}✗ FAIL${COLOR_RESET}: $1"
    ((FAILED++))
}

warn() {
    echo -e "${COLOR_YELLOW}⚠ WARN${COLOR_RESET}: $1"
    ((WARNINGS++))
}

info() {
    echo -e "${COLOR_BLUE}ℹ INFO${COLOR_RESET}: $1"
}

separator() {
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "$1"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
}

# Main verification
separator "🔍 Linux Wallpaper Engine Startup Service Verification"

# 1. Check if service file exists
separator "1. Service File Check"
SERVICE_FILE="$HOME/.config/systemd/user/linux-wallpaperengine.service"
if [ -f "$SERVICE_FILE" ]; then
    pass "Service file exists"
else
    fail "Service file not found"
fi

# 2. Check if service is enabled
separator "2. Service Enable Status"
if systemctl --user is-enabled linux-wallpaperengine.service > /dev/null 2>&1; then
    pass "Service is enabled (auto-start on login)"
else
    warn "Service is disabled (will not auto-start on login)"
fi

# 3. Check current service status
separator "3. Current Service Status"
if systemctl --user is-active linux-wallpaperengine.service > /dev/null 2>&1; then
    pass "Service is currently active"
else
    warn "Service is not currently active (normal between restarts)"
fi

# 4. Check if startup script exists
separator "4. Startup Handler Script"
HANDLER_SCRIPT="$HOME/lwe-expanded-features-GUI/source/core/startup_handler.sh"
if [ -f "$HANDLER_SCRIPT" ]; then
    pass "Handler script exists"
    
    # Check if executable
    if [ -x "$HANDLER_SCRIPT" ]; then
        pass "Handler script is executable"
    else
        fail "Handler script is NOT executable"
    fi
else
    fail "Handler script not found"
fi

# 5. Check if startup manager exists
separator "5. Startup Manager Script"
MANAGER_SCRIPT="$HOME/lwe-expanded-features-GUI/source/core/startup_manager.py"
if [ -f "$MANAGER_SCRIPT" ]; then
    pass "Manager script exists"
else
    fail "Manager script not found"
fi

# 6. Check configuration
separator "6. Configuration File"
CONFIG_FILE="$HOME/.config/linux-wallpaper-engine/config.json"
if [ -f "$CONFIG_FILE" ]; then
    pass "Configuration file exists"
    
    # Check if startup is enabled
    if grep -q '"__run_at_startup__": true' "$CONFIG_FILE" 2>/dev/null; then
        pass "Startup is ENABLED in configuration"
    else
        warn "Startup is DISABLED in configuration"
    fi
else
    warn "Configuration file not found"
fi

# 7. Check log directory
separator "7. Log Directory"
LOG_DIR="$HOME/.local/share/linux-wallpaper-engine-features"
if [ -d "$LOG_DIR" ]; then
    pass "Log directory exists"
else
    warn "Log directory not found (will be created on first run)"
fi

# 8. Check log file
separator "8. Log File"
LOG_FILE="$LOG_DIR/logs.txt"
if [ -f "$LOG_FILE" ]; then
    pass "Log file exists"
    
    # Check if recent logs exist
    RECENT_LOGS=$(grep -c "STARTUP" "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$RECENT_LOGS" -gt 0 ]; then
        pass "Found $RECENT_LOGS startup log entries"
    else
        warn "No startup log entries found yet"
    fi
else
    warn "Log file not found (will be created on startup)"
fi

# 9. Check main.sh script
separator "9. Main Engine Script"
MAIN_SCRIPT="$HOME/lwe-expanded-features-GUI/source/core/main.sh"
if [ -f "$MAIN_SCRIPT" ]; then
    pass "Main script exists"
    
    if [ -x "$MAIN_SCRIPT" ]; then
        pass "Main script is executable"
    else
        warn "Main script may not be executable"
    fi
else
    fail "Main script not found"
fi

# 10. Check wallpaper engine binary
separator "10. Wallpaper Engine Binary"
ENGINE_BINARY="$HOME/lwe-expanded-features-GUI/linux-wallpaperengine/build/output/linux-wallpaperengine"
if [ -f "$ENGINE_BINARY" ]; then
    pass "Engine binary exists"
else
    warn "Engine binary not found"
fi

# 11. Recent service activity
separator "11. Recent Service Activity"
if [ -f "$LOG_FILE" ]; then
    LAST_RUN=$(tail -1 "$LOG_FILE" 2>/dev/null)
    if [ -n "$LAST_RUN" ]; then
        info "Last log: $LAST_RUN"
    fi
    
    # Check if there are any errors
    ERROR_COUNT=$(grep -c "ERROR\|FATAL" "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        warn "Found $ERROR_COUNT error entries in logs"
    else
        pass "No error entries in logs"
    fi
fi

# Summary
separator "📊 Verification Summary"
echo -e "${COLOR_GREEN}Passed:${COLOR_RESET}   $PASSED"
echo -e "${COLOR_RED}Failed:${COLOR_RESET}   $FAILED"
echo -e "${COLOR_YELLOW}Warnings:${COLOR_RESET} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${COLOR_GREEN}✓ All checks passed! Service is healthy.${COLOR_RESET}"
    else
        echo -e "${COLOR_YELLOW}⚠ Checks passed with warnings. Review above.${COLOR_RESET}"
    fi
else
    echo -e "${COLOR_RED}✗ Some checks failed. Review errors above.${COLOR_RESET}"
fi
