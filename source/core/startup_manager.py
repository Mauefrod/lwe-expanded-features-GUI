import subprocess
import sys
from pathlib import Path

# This file is in source/core/
SCRIPT_DIR = Path(__file__).parent.absolute()
CORE_DIR = SCRIPT_DIR  # source/core/
SOURCE_DIR = CORE_DIR.parent  # source/
GUI_DIR = SOURCE_DIR / "gui"

# Add gui directory to path for imports
sys.path.insert(0, str(GUI_DIR))

from config import load_config, build_args

def run_at_startup():
    config = load_config()
    
    if not config.get("run_at_startup", False):
        print("[INFO] Run at startup is disabled")
        return
    
    args = build_args(config, log_callback=print)
    
    if not args:
        print("[WARNING] No valid arguments to run")
        return
    
    # main.sh is in source/core/
    main_script = CORE_DIR / "main.sh"
    cmd = [str(main_script)] + args
    print(f"[INFO] Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to run wallpaper engine: {e}", file=sys.stderr)
        sys.exit(1)