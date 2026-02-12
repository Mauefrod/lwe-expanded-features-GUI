from gui.gui_engine import WallpaperEngineGUI
import sys
import traceback

if __name__ == "__main__":
    try:
        app = WallpaperEngineGUI()
        app.run()
    except KeyboardInterrupt:
        print("[GUI] Application interrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"[GUI] FATAL ERROR: {str(e)}", file=sys.stderr)
        print(f"[GUI] Traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)