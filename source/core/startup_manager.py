
"""
Startup Manager for Linux Wallpaper Engine
Handles application startup with saved configuration
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from ..common.constants import MAIN_SCRIPT_NAME

# This hardcoded values could become an issue if you are working with custom envs. 
# That being said, the main purpose of the whole "core" module is so that you can 
# either run the app from the terminal via {MAIN_SCRIPT_NAME} / run.sh or so that when it comes to
# coding you don't need to change the constants in the files, so consider this a burden
# you have to bear when it comes to development.
# Either that or refactor those modules or the constants... in which case, they are not 
# constants. :)

# Be wary that I don't have a full logging class to handle all the scenarios you might want to log,
# The logging is written with agent and I mostly handled common cases and some edge cases, 
# I don't plan on expanding it since it's out of scope.

SCRIPT_DIR = Path(__file__).parent.absolute()
CORE_DIR = SCRIPT_DIR
SOURCE_DIR = CORE_DIR.parent
GUI_DIR = SOURCE_DIR / "gui"


if not GUI_DIR.exists():
    print(f"[FATAL ERROR] GUI directory not found: {GUI_DIR}")
    sys.exit(1)


sys.path.insert(0, str(SOURCE_DIR))
sys.path.insert(0, str(GUI_DIR))
sys.path.insert(0, str(CORE_DIR))

# You can set this logger to None if you don't want to log the startup process, but again... why??
# You can also set custom callbacks using the logger functions in the common module... in case you do it,
# Open an issue and I will provide support for it given that I like its implementation.
LOG_DIR = Path.home() / ".local" / "share" / "linux-wallpaper-engine-features"
LOG_FILE = LOG_DIR / "logs.txt"


def log_to_file(message):
    """Write log message to file"""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}", file=sys.stderr)


def log(message):
    """Log to both console and file"""
    print(message)
    log_to_file(message)


def validate_environment():
    """Validate that required environment variables are set"""
    log("[STARTUP] Validating environment...")

    errors = []

    if not os.environ.get("DISPLAY"):
        errors.append("DISPLAY is not set")

    if not os.environ.get("XAUTHORITY"):
        """I don't plan on explaining what XAUTHORITY is, in case you are a dev and have found bugs
        in the startup process, but don't know what XAUTHORITY is, go read it's documentation, it's
        really important when working with X11 and Desktop Environments on Linux.
        If you are not a developer, and have found an XAUTHORITY error, open and issue and I will flag
        it as high priority. 
        
        DO NOT TRY TO SET XAUTHORITY AS AN ENV VARIABLE, I WON'T SUPPORT IT AT ALL"""
        
        errors.append("XAUTHORITY is not set (X11 may not be available)")

    main_script = CORE_DIR / MAIN_SCRIPT_NAME
    if not main_script.exists():
        errors.append(f"{MAIN_SCRIPT_NAME} not found: {main_script}")

    if errors:
        log("[WARNING] Environment issues detected:")
        for error in errors:
            log(f"  - {error}")
        return False

    log("[STARTUP] Environment validation passed")
    return True






def run_at_startup():
    """Main startup function"""
    try:
        from gui.config import load_config, build_args
    except ImportError as e:
        log(f"[FATAL ERROR] Failed to import config module: {e}")
        sys.exit(1)

    log("[STARTUP] ========== Linux Wallpaper Engine Startup ==========")
    log(f"[STARTUP] Working directory: {CORE_DIR}")
    log(f"[STARTUP] User: {os.environ.get('USER', 'unknown')}")
    log(f"[STARTUP] Python: {sys.version.split()[0]}")

    if not validate_environment():
        log("[WARNING] Some environment variables are missing, continuing anyway...")

    try:
        config = load_config()
    except Exception as e:
        log(f"[ERROR] Failed to load configuration: {e}")
        sys.exit(1)

    log("[STARTUP] Configuration loaded successfully")

    if not config.get("__run_at_startup__", False):
        log("[INFO] Run at startup is disabled - exiting gracefully")
        return

    log("[STARTUP] Configuration details:")
    log(f"[STARTUP]   Directory: {config.get('--dir', 'Not set')}")
    log(f"[STARTUP]   Window mode: {config.get('--window', {}).get('active', False)}")
    log(f"[STARTUP]   Above flag: {config.get('--above', False)}")
    log(f"[STARTUP]   Random mode: {config.get('--random', False)}")
    log(f"[STARTUP]   Delay mode: {config.get('--delay', {}).get('active', False)}")
    if config.get('--delay', {}).get('active', False):
        log(f"[STARTUP]   Delay timer: {config.get('--delay', {}).get('timer', '0')} seconds")
    log(f"[STARTUP]   Set wallpaper: {config.get('--set', {}).get('wallpaper', 'Not set')}")
    log(f"[STARTUP]   Sound silent: {config.get('--sound', {}).get('silent', False)}")
    pool_size = len(config.get('--pool', []))
    log(f"[STARTUP]   Pool size: {pool_size} wallpapers")

    try:
        args = build_args(config, log_callback=log)
    except Exception as e:
        log(f"[ERROR] Failed to build arguments: {e}")
        sys.exit(1)

    if not args:
        log("[WARNING] No valid arguments to run")
        log("[WARNING] Please configure a valid wallpaper directory")
        return

    main_script = CORE_DIR / MAIN_SCRIPT_NAME 
    # You could say this is a hardcoded value, if that's an issue for you,
    # you can set the LWE_SCRIPT_DIR env variable to point to the directory containing the script
    # regardless, like I said before, the main purpose of the whole "core" module is so that you can either run the app 
    # from the terminal via main.sh or run.sh, so you do you.

    if not main_script.exists():
        log(f"[FATAL ERROR] Script not found: {main_script}")
        sys.exit(1)

    try:
        mode = main_script.stat().st_mode
        if not (mode & 0o111):
            log(f"[INFO] Making script executable: {main_script}")
            main_script.chmod(mode | 0o111)
    except Exception as e:
        log(f"[WARNING] Failed to set executable permissions: {e}")


    cmd = [str(main_script)] + args
    cmd_str = " ".join(cmd)
    log(f"[STARTUP] Executing command:")
    log(f"[STARTUP]   {cmd_str}")
    log("[STARTUP] =========================================================")

    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            cwd=str(CORE_DIR)
        )

        if result.stdout:
            log(f"[STARTUP] Output:\n{result.stdout}")
        if result.stderr:
            log(f"[STARTUP] Stderr:\n{result.stderr}")

        if result.returncode == 0:
            log("[STARTUP] Wallpaper engine started successfully")
            return
        else:
            log(f"[WARNING] Command exited with code {result.returncode}")
            log("[WARNING] This may be normal if the engine daemonizes")
            return

    except subprocess.CalledProcessError as e:
        log(f"[ERROR] Failed to run wallpaper engine")
        log(f"[ERROR] Return code: {e.returncode}")
        if e.stdout:
            log(f"[ERROR] Stdout: {e.stdout}")
        if e.stderr:
            log(f"[ERROR] Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        log(f"[FATAL ERROR] Script not found: {main_script}")
        sys.exit(1)
    except Exception as e:
        log(f"[FATAL ERROR] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        log(f"[FATAL ERROR] Traceback:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        run_at_startup()
    except KeyboardInterrupt:
        # I don't know if this is even remotely possible, 
        # But in the chance that you are running the startup script from the terminal,
        # Or you set some weird keyboard shortcut to run / stop it, this should be good enough,
        # If it isn't, open and issue and i will provide you documenation of the built keyboard API,
        # Or provide support altogether :)
        log("[STARTUP] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        log(f"[FATAL ERROR] Unhandled exception: {e}")
        import traceback
        log(f"[FATAL ERROR] Traceback:\n{traceback.format_exc()}")
        sys.exit(1)